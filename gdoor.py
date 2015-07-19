# Add your own MAC address below and replace AA:BB:CC:DD:FF:GG
# Split the nmap feature into a separate routine (def) so
# that it can be summoned by check_open & check_phones.

import datetime
import os
import pifacedigitalio
import time

print "Starting Garage Door Script"
# Create & Init a PiFace Digtal object
pfd = pifacedigitalio.PiFaceDigital()
pifacedigitalio.init()

################################
### Create default variables ###
################################
gdoor_closed = pfd.input_pins[7].value
gdoor_open = pfd.input_pins[6].value
gdoor_curfew = True
gdoor_lock = False

j_away = False
j_away_previous = False

ok_to_open = False
ok_to_close = False
partially_open = 1
retry = 3
var = " "

# Ensure off is lower than on times.
curfew_off = datetime.time(7,30).strftime("%H:%M:%S") # 24-hour clock req'd
curfew_on = datetime.time(20,30).strftime("%H:%M:%S") # 24-hour clock req'd

timer1 = (datetime.datetime.now()).strftime("%H:%M:%S")
timer2 = (datetime.datetime.now()).strftime("%H:%M:%S")
timer2b = False
timer_minutes = 20

	#################
	### Functions ###
	#################

# Decide if the curfew is on or off
def check_curfew():
	global curfew_off, current_time, curfew_on, gdoor_curfew, ok_to_open, j_away_previous
	
	if curfew_off <= current_time <= curfew_on:
		gdoor_curfew = False
	
	else:
		gdoor_curfew = True
		ok_to_open = False
		j_away_previous = False

# Checks the status of the Garage Door. If no lock is set, a timer is 
# started to close the Garage Door. If no one is home, the 
# door will shut immediately. NEED TO RUN NMAP TO CHECK FOR PHONES

# The circuit is a 5V/Open circuit. 
# If the door is fully close, gdoor_closed will be true.
# If the door is fully open, gdoor_open will be true.
# If it's in the middle, both variables will be false.
# Both true, should be impossible. It should indicate an error.
def check_open():
	global gdoor_open, gdoor_closed, gdoor_lock, j_away, timer_10, ok_to_close

	gdoor_closed = pfd.input_pins[6].value
	gdoor_open = pfd.input_pins[7].value

	#simulate gdoor_lock with a switch. gdoor_lock should be set through a webpage
	#gdoor_lock = pfd.input_pins[2].value
	
	# Garage door is fully closed
	if gdoor_closed == True and gdoor_open == False:
			#print "gdoor_closed is true, trying to reset time."
			timer_10 = datetime.time(0,00).strftime("%H:%M:%S")
			ok_to_close = False
	
	# Garage door is fully open
	elif gdoor_open == True and gdoor_closed == False:
		#print "gdoor_open is true"
		#if gdoor_lock == True and j_away == True:
			##if j_away == True: # add "or p_away "
			##print "closing garage door because both owners left."
			#push_button(0.5)
			#time.sleep(20)
			#gdoor_lock = False
			#ok_to_close = False
			## Check to see if door really closed
		#elif gdoor_lock == True and j_away == False:
			#print "The door has been locked open & the owner is home"
		#	ok_to_close = False
		else:
			if ok_to_close == True:
				if timer_10 < current_time:
					#print "Closing garage door because owners are home but didn't lock door open"
					push_button(0.5)
					ok_to_close = False
					time.sleep(30)
					# wait 30sec, check if door is closed
			else:
				timer_10 = (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%H:%M:%S")
				ok_to_close = True
				#print "Setting timer for 10 minutes because door is not locked open"
	
	# Garage door is somewhere in the middle. We don't know if the 
	# door will go up or down. We will press the button, wait, then check.
	# If the door is not fully closed, we'll try to close the door.
	elif gdoor_open == False:
		

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
			print "Retries Gone!"
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

# function pushes the garage door switch for the specified "push_time"	
def push_button(push_time):
	pfd.leds[0].toggle()
	time.sleep(push_time)
	pfd.leds[0].toggle()

def garage_open():
	global partially_open
	gdoor_closed = pfd.input_pins[6].value
	gdoor_open = pfd.input_pins[7].value
	print "closed switch =", gdoor_closed
	print "  open switch =", gdoor_open
	print " "

	while gdoor_open == False and gdoor_closed == False:
		gdoor_closed = pfd.input_pins[6].value
		gdoor_open = pfd.input_pins[7].value
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
while True:
	current_time = (datetime.datetime.now()).strftime("%H:%M:%S")
	check_curfew()
	
	if gdoor_curfew == False:
		check_phones()
	
	# check_open()
	
	# Reduce CPU load by including a delay. Delay can be safely removed and Pi will work fine.
	# Possible downside may include increased phone battery consumption.
	if j_away == False:
		time.sleep(60)
	else:
		time.sleep(.5)
