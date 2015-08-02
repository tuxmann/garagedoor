#       INSTRUCTIONS
# 1.    Comment out the GPIO or pfd portion that is not used so errors are not produced.
# 2.    Assign the right pin to the switch.

import time
import os
import RPi.GPIO as GPIO
import pifacedigitalio

# Create & Init a PiFace Digtal object
pfd = pifacedigitalio.PiFaceDigital()

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(22, GPIO.LOW)
GPIO.cleanup()

# Close relay 0 for 0.5 seconds
pfd.leds[0].toggle()
time.sleep(0.5)
pfd.leds[0].toggle()
