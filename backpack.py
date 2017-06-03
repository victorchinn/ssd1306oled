#!/usr/bin/python
# =============================================================================
#        File : bmp280.py
# Description : Read data from the Bosch digital pressure sensor.
#      Author : S. Dame (Adapted from Matt Hawkins' code)
#        Date : 12/21/2016
# Touched - 05-27-2017
# =============================================================================
#
#  Official datasheet available from :
#  https://www.bosch-sensortec.com/bst/products/all_products/bme280
#
# Matt Hawkin's site --> http://www.raspberrypi-spy.co.uk/
# =============================================================================
import smbus    # System Management Bus
import time     # time utilities

# =============================================================================
# ctypes is an advanced ffi (Foreign Function Interface) package for Python
# that provides  call functions in dlls/shared libraries and has extensive
# facilities to create, access and manipulate simple and complicated
# C data types in Python
# =============================================================================
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte


# =============================================================================
# following is required for SSD1306OLED to be controlled in Adafruit Library
import RPi.GPIO as GPIO

import time

import Adafruit_GPIO.SPI as SPI
import ssd1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
# =============================================================================

# =============================================================================
# FOR IFTTT event to fire
import httplib
import base64
import sys

# IFTTT_KEY = 'bo6U0C7dVkHlc0xRaeE6II'
# dIG-vsAAZWsdP4NeHxsbcA #
IFTTT_KEY = 'bLat1rLymZHak1SpVDdH6t'

PORT      = 443
URL       = 'maker.ifttt.com'
API       = '/trigger/over_temperature/with/key/' + IFTTT_KEY
# FOR IFTTT event to fire
# =============================================================================



# =============================================================================
# create a sensor object
# -----------------------------------------------------------------------------

DEVICE = 0x76

class PiBMP280(object):
    """Raspberry Pi 'IoT BMP280 Sensor'."""

    # addr = I2C Chip Address
    def __init__(self,addr=DEVICE):
        self.bus = smbus.SMBus(1)   # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                                    # Rev 1 Pi uses bus 0
        self.addr = addr            # register the address with the object

    def readBMP280ID(self):
      REG_ID     = 0xD0
      (chip_id, chip_version) = self.bus.read_i2c_block_data(self.addr, REG_ID, 2)
      return (chip_id, chip_version)

    def readBMP280All(self, addr=DEVICE):
      # Register Addresses
      REG_DATA = 0xF7
      REG_CONTROL = 0xF4
      REG_CONFIG  = 0xF5

      # Oversample setting - page 27
      OVERSAMPLE_TEMP = 2
      OVERSAMPLE_PRES = 2
      MODE = 1

      # write oversample configuration and mode
      control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
      self.bus.write_byte_data(self.addr, REG_CONTROL, control)

      # Read blocks of calibration data from EEPROM
      # See Page 22 data sheet
      cal1 = self.bus.read_i2c_block_data(self.addr, 0x88, 24)
      cal2 = self.bus.read_i2c_block_data(self.addr, 0xA1, 1)
      cal3 = self.bus.read_i2c_block_data(self.addr, 0xE1, 7)

      # Convert byte data to word values
      dig_T1 = getUShort(cal1, 0)
      dig_T2 = getShort(cal1, 2)
      dig_T3 = getShort(cal1, 4)

      dig_P1 = getUShort(cal1, 6)
      dig_P2 = getShort(cal1, 8)
      dig_P3 = getShort(cal1, 10)
      dig_P4 = getShort(cal1, 12)
      dig_P5 = getShort(cal1, 14)
      dig_P6 = getShort(cal1, 16)
      dig_P7 = getShort(cal1, 18)
      dig_P8 = getShort(cal1, 20)
      dig_P9 = getShort(cal1, 22)

    #   dig_H1 = getUChar(cal2, 0)
    #   dig_H2 = getShort(cal3, 0)
    #   dig_H3 = getUChar(cal3, 2)
      #
    #   dig_H4 = getChar(cal3, 3)
    #   dig_H4 = (dig_H4 << 24) >> 20
    #   dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)
      #
    #   dig_H5 = getChar(cal3, 5)
    #   dig_H5 = (dig_H5 << 24) >> 20
    #   dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

    #   dig_H6 = getChar(cal3, 6)

      data = self.bus.read_i2c_block_data(self.addr, REG_DATA, 6)
      pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
      temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

      # Refine temperature based on calibration per spec
      var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
      var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
      t_fine = var1+var2
      temperature = float(((t_fine * 5) + 128) >> 8);

      # Refine pressure and adjust for temperature
      var1 = t_fine / 2.0 - 64000.0
      var2 = var1 * var1 * dig_P6 / 32768.0
      var2 = var2 + var1 * dig_P5 * 2.0
      var2 = var2 / 4.0 + dig_P4 * 65536.0
      var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
      var1 = (1.0 + var1 / 32768.0) * dig_P1
      if var1 == 0:
        pressure=0
      else:
        pressure = 1048576.0 - pres_raw
        pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
        var1 = dig_P9 * pressure * pressure / 2147483648.0
        var2 = pressure * dig_P8 / 32768.0
        pressure = pressure + (var1 + var2 + dig_P7) / 16.0

      return temperature/100.0,pressure/100.0



def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
  result = data[index]
  if result > 127:
    result -= 256
  return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
  result =  data[index] & 0xFF
  return result

# =============================================================================
# this method gets called when an overtemperature triggers ... 
# using IFTTT send the over_temperature event trigger which (web action) that sends an sms message to my cell phone
#
def overtemp_event():
  
  conn = httplib.HTTPSConnection(URL, PORT)

  conn.request('GET', API)
  r1 = conn.getresponse()
  print "status " + str(r1.status) + ", reason " + str(r1.reason)
  data1 = r1.read()
  print "data: " + str(data1)
  conn.close()
  
  return 



# Raspberry Pi pin configuration:
RST = 24

# =============================================================================
# main to test from CLI
def main():

    # get the SSD1306OLED ready by initializing it then clear the display

    # 128x64 display with hardware I2C:
    disp = ssd1306.SSD1306_128_64(rst=RST)
    # Initialize library.
    disp.begin()

    # Clear display.
    disp.clear()
    disp.display()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # =============================================================================
    # create an instance of my pi bmp280 sensor object
    pi_bmp280 = PiBMP280()
    
    # Read the Sensor ID.
    (chip_id, chip_version) = pi_bmp280.readBMP280ID()
    print "    Chip ID :", chip_id
    print "    Version :", chip_version

    while (1):
        # Read the Sensor Temp/Pressure values.
        (temperature, pressure) = pi_bmp280.readBMP280All()
        print "Temperature :", temperature, "C"
        print "   Pressure :", pressure, "hPa"

        # =============================================================================
        # Load default font.
        font = ImageFont.load_default()
 
        # Alternatively load a TTF font.
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        #font = ImageFont.truetype('Minecraftia.ttf', 24)
        # Write two lines of text.
        draw.text((0, 0),  'T = ' + str(temperature) + ' C', font=font, fill=128)
        draw.text((0, 20), 'P = ' + str(pressure) + ' hPa' , font=font, fill=255)
    
        # Display image.
        disp.image(image)
        disp.display()
        time.sleep(0.01)
        # Draw a black filled box to clear the image else redrawn text clutters display and makes text unreadable
        draw.rectangle((0,0,width,height), outline=0, fill=0)

      
      # =============================================================================

        # if over temperature then send IFTTT and stop
        if (temperature >=27):
          overtemp_event()
          break

if __name__=="__main__":
   main()
