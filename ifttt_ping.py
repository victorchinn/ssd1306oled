#!/usr/bin/python
# =============================================================================
#        File : ifttt_ping.py
# Description : Allows pinging
#      Author : Drew Gislsason
#        Date : 5/16/2017
# =============================================================================
import httplib
import base64
import sys

# IFTTT_KEY = 'bo6U0C7dVkHlc0xRaeE6II'
# dIG-vsAAZWsdP4NeHxsbcA #
IFTTT_KEY = 'bLat1rLymZHak1SpVDdH6t'

PORT      = 443
URL       = 'maker.ifttt.com'
API       = '/trigger/over_temperature/with/key/' + IFTTT_KEY

conn = httplib.HTTPSConnection(URL, PORT)

conn.request('GET', API)
r1 = conn.getresponse()
print "status " + str(r1.status) + ", reason " + str(r1.reason)
data1 = r1.read()
print "data: " + str(data1)
conn.close()
