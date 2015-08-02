# INSTRUCTIONS:
# 1. 	This code allows for GPIO or PiFace Digital to be used
#	Comment out code you don't need.
# 2.	Add your own MAC address below and replace AA:BB:CC:DD:FF:GG
# 3.	Adjust Curfew time to suit your needs.

import datetime
import os
import pifacedigitalio
import RPi.GPIO as GPIO
import time

# Create & Init a PiFace Digtal object
pfd = pifacedigitalio.PiFaceDigital()
pifacedigitalio.init()

# Create & Init RPi GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.OUT)


################################
### Create default variables ###
################################
# IF YOU CHANGE THIS, CHANGE THE get_status() FUNCTION TOO!!!
# RPi.GPIO inputs will be inverted for the debugging convenience.
gdoor_closed = pfd.input_pins[7].value			# For PiFace Digital Interface
gdoor_open = pfd.input_pins[6].value			# For PiFace Digital Interface
gdoor_closed = not GPIO.input(13)			# For RPi GPIO Interface
gdoor_open = not GPIO.input(11)				# For RPi GPIO Interface

gdoor_curfew = True
gdoor_lock = False

j_away = False
j_away_previous = False

ok_to_open = False
ok_to_close = False
partially_open = 1
retry = 3
status_count = 0
var = " "

# Ensure off is lower than on times.
curfew_off = datetime.time(7,30).strftime("%H:%M:%S") # 24-hour clock req'd
curfew_on = datetime.time(20,30).strftime("%H:%M:%S") # 24-hour clock req'd

timer1 = (datetime.datetime.now()).strftime("%H:%M:%S")
timer2 = (datetime.datetime.now()).strftime("%H:%M:%S")
timer2b = False
timer_minutes = 20

###################################
### 	  Functions 		###
###################################

# Get the status of the Garage Door. If no lock is set, a timer is 
# started to close the Garage Door. If no one is home, the 
# door will shut immediately. NEED TO RUN NMAP TO CHECK FOR PHONES

# The owner comes home and presses the button for the garage door before
# the phone is detected, we will do nothing if the door is going up.

def check_open():
	global gdoor_open, gdoor_closed, gdoor_lock, j_away, timer1, ok_to_close, status_count

	get_status()
	
	# Garage door is in the middle
	if gdoor_closed == False and gdoor_open == False:
		if status_count > 0:
			status_count = status_count + 1
			print status_count
		if status_count < 0:
			status_count = status_count - 1
			print status_count
		if status_count > 30:
			print "stuck in middle"
		if status_count < -30:
			print "stuck in middle"
	
	# Garage door is fully closed
	elif gdoor_closed == True and gdoor_open == False:
		print "gdoor_closed is true"
		timer1 = datetime.time(0,00).strftime("%H:%M:%S")
		#ok_to_close = False
		status_count = -1 
	# Garage door is fully open
	elif gdoor_open == True and gdoor_closed == False:
		print "gdoor_open is true"
		status_count = 1
		

# Scanning only one IP addr or a limited number of IP addr is significantly faster.
# Running nmap and scanning all 255 addr was taking upwards of 5 seconds or longer.
def check_phones():
	global gdoor_curfew, timer2b, j_away, j_away_previous, retry, timer2, ok_to_open
	
	# Var will come back with the MAC address or the response will be empty.
	# The name var is required and can't be changed into a different name.
	var = os.popen('sudo nmap -sP 192.168.1.3 | grep AA:BB:CC:DD:FF:GG').read()
	if var != "" and ok_to_open == True:
		print" "
		print datetime.datetime.now()
		if -30 < status_count < -1:
			print "Door is in the process of opening..."
		if  status_count == -1:
			print "Opening door for the owner of the phone. Come in."
			garage_open()
		ok_to_open = False
	# Run nmap three or more times to verify the phone is really off the network.
	while var == "": 
		var = os.popen('sudo nmap -sP 192.168.1.3 | grep AA:BB:CC:DD:FF:GG').read()
		if var == "" and retry >= 0:
			print "Decrementing Retries"
			retry = retry - 1
			time.sleep(0.5)
		if retry <= 0:
			#print "Retries Gone!"
			j_away = True
			# Check if the current time is past the trigger time.
			if j_away == j_away_previous and ok_to_open == False and timer2 < current_time:
				ok_to_open = True
				print "THE TIMER IS FINISHED!"
			elif j_away_previous == False:
				print " "
				print datetime.datetime.now()
				print "Creating a timer. The phone has left."
				timer2 = (datetime.datetime.now() + datetime.timedelta(minutes=timer_minutes)).strftime("%H:%M:%S")
				j_away_previous = True
			break	
	# The phone is home and it's not ok to open the garage door automatically.
	if var != "" and ok_to_open == False:
		retry = 3
		j_away = False
		j_away_previous = False

def get_status():
	global gdoor_open, gdoor_closed
	gdoor_closed = pfd.input_pins[7].value		# For PiFace Digital Interface
	gdoor_open = pfd.input_pins[6].value		# For PiFace Digital Interface
	gdoor_closed = not GPIO.input(13)			# For RPi GPIO Interface
	gdoor_open = not GPIO.input(11)				# For RPi GPIO Interface
	
# function pushes the garage door switch for the specified "push_time"	
def push_button(push_time):
	pfd.leds[0].toggle()
	GPIO.output(22, GPIO.HIGH)
	time.sleep(push_time)
	GPIO.output(22, GPIO.LOW)
	pfd.leds[0].toggle()

def garage_open():
	global partially_open
	get_status()
	print "closed = %d, open = %d" % (gdoor_closed, gdoor_open)
	print " "

	while gdoor_open == False and gdoor_closed == False:
		get_status()
		time.sleep(0.2)
		if partially_open == True:
			print "Door stuck in the middle, pressed door switch"
			push_button(0.5)
			partially_open = 0
	
		if gdoor_closed == True and gdoor_open == False:
			print "Door closed, opening door now."
			push_button(2)		# Introduce enough delay for the sensors to change state
			partially_open = 1
		
		if gdoor_closed == False and gdoor_open == True:
			print "Door already open, nothing to do"
			partially_open = 1
	if gdoor_open == False and gdoor_closed == True:
		push_button(0.5)


# Start main program and keep looping 
print "Starting Garage Door Script"

while True:
	current_time = (datetime.datetime.now()).strftime("%H:%M:%S")
	check_open()
	
	if curfew_off <= current_time <= curfew_on:	# Curfew is off
		check_phones()
	
	else:										# Curfew is on
		ok_to_open = False
		j_away_previous = False

	# Reduce CPU load by including a delay. Delay can be safely removed and Pi will work fine.
	# Possible downside may include increased phone battery consumption.
	if j_away == False:
		time.sleep(60)
	else:
		time.sleep(.5)
