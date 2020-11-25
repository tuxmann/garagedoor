import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(8, GPIO.OUT)
GPIO.output(8, GPIO.LOW)

print("LEDs on daughter board should be off now.")
