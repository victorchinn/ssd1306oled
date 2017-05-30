#
#
# Use GPIO as needed
import RPi.GPIO as GPIO

# Use Time
import time

# Use both libraries from Adafruit for GPIO and SSD1306 OLED display
import Adafruit_GPIO.SPI as SPI
import ssd1306

# Use Pixel Library
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


## Input pins:
#L_pin = 27 
#R_pin = 23 
#C_pin = 4 
#U_pin = 17 
#D_pin = 22 
#
#A_pin = 5 
#B_pin = 6 


GPIO.setmode(GPIO.BCM) 

#GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
#GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up


# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
#DC = 23
#SPI_PORT = 0
#SPI_DEVICE = 0


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

try:
	# Load default font.
	font = ImageFont.load_default()
 
	# Alternatively load a TTF font.
	# Some other nice fonts to try: http://www.dafont.com/bitmap.php
	#font = ImageFont.truetype('Minecraftia.ttf', 8)
 
	# Write two lines of text.
	draw.text((0, 0),  'Hello',  font=font, fill=255)
	draw.text((0, 20), 'World!', font=font, fill=255)

	# Display image.
	disp.image(image)
	disp.display()
	time.sleep(.01) 


except KeyboardInterrupt: 
    GPIO.cleanup()

