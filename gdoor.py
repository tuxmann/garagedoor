# Add your own MAC address below and replace AA:BB:CC:DD:FF:GG
# Split the nmap feature into a separate routine (def) so
# that it can be summoned by check_open & check_phones.

import datetime
import os
import pifacedigitalio
import time

# Create & Init a PiFace Digtal object
pfd = pifacedigitalio.PiFaceDigital()
pifacedigitalio.init()


# Create default variables
gdoor_closed = pfd.input_pins[1].value
gdoor_open = pfd.input_pins[0].value
gdoor_lock = False

# Set curfew here. Ensure off is lower than on times.
# datetime.time(HOUR, MIN) and requires military time.
curfew_off = datetime.time(7,30).strftime("%H:%M:%S")
curfew_on = datetime.time(20,30).strftime("%H:%M:%S")
gdoor_curfew = True

ok_to_close = False
timer_10 = (datetime.datetime.now()).strftime("%H:%M:%S")
timer_20b = False
timer_20 = (datetime.datetime.now()).strftime("%H:%M:%S")

var = " "
j_away = False
j_away_previous = False
ok_to_open = False
#p_away = False
#Wife's iPhone 5S doesn't reliably stay on Wifi

# Determine if the current time is ok to let the 
# door open automatically
def check_curfew():
	global curfew_off, current_time, curfew_on, gdoor_curfew, ok_to_open, j_away_previous
	if curfew_off <= current_time <= curfew_on:
		gdoor_curfew = False
	else:
		# Set curfew to True to prevent Phone checking.
		gdoor_curfew = True
		# Set ok_to_open to false to prevent the door from opening once
		# the curfew is off if owner leaves before curfew is on
		ok_to_open = False
		# Set j_away_previous to false to ensure that door will open if 
		# owner leaves before curfew starts, comes home during curfew 
		# and leaves before curfew ends
		j_away_previous = False

# Checks the status of the Garage Door to see if it's fully open or
# fully closed. If no lock is set, a 10 min timer is started to close
# the Garage Door. If no one is home, the door will shut immediately.
# NEED TO RUN NMAP TO CHECK FOR PHONES
def check_open():
	global gdoor_open, gdoor_closed, gdoor_lock, j_away, timer_10, ok_to_close
	# print " "
	# print "Running check_open routing"

	#simulate gdoor_lock with a switch. gdoor_lock should be set through a webpage
	#gdoor_lock = pfd.input_pins[2].value
	gdoor_open = pfd.input_pins[0].value
	gdoor_closed = pfd.input_pins[1].value # needs to send status to webpage
        if gdoor_closed == True:
                #print "gdoor_closed is true, trying to reset time."
                timer_10 = datetime.time(0,00).strftime("%H:%M:%S")
                ok_to_close = False
	elif gdoor_open == True:
		#print "gdoor_open is true"
		if gdoor_lock == True and j_away == True:
			#if j_away == True: # add "or p_away "
			#print "closing garage door because both owners left."
			garage_toggle()
			time.sleep(10)
			gdoor_lock = False
			ok_to_close = False
			# Check to see if door really closed
		elif gdoor_lock == True and j_away == False:
			#print "The door has been locked open & the owner is home"
			ok_to_close = False
		else:
			if ok_to_close == True:
				if timer_10 < current_time:
					#print "closing garage door because owners are home but didn't lock door open"
					garage_toggle()
					ok_to_close = False
					time.sleep(30)
					# wait 30sec, check if door is closed
			else:
				timer_10 = (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%H:%M:%S")
				ok_to_close = True
				#print "Setting timer for 10 minutes because door is not locked open"

# Scanning only one IP addr or a limited number of IP addr is significantly faster.
# Running nmap and scanning all 255 addr was taking upwards of 5 seconds or longer.
def check_phones():
	global gdoor_curfew, timer_20b, j_away, j_away_previous, timer_20, ok_to_open
	# If the curfew is active, checking for phones will be skipped.
	if gdoor_curfew == False:
		# Var will come back with the MAC address or the response will be empty.
		# The name Var is required and can't be changed into a different name.
		var = os.popen('sudo nmap -sP 192.168.1.3 | grep AA:BB:CC:DD:FF:GG').read()
		if var != "" and ok_to_open == True:
			#print "Opening door for the owner of the phone. Come in."
			garage_toggle()
			ok_to_open = False
		elif var == "": 
			# I'D LIKE TO FIND A BETTER WAY TO CHECK 3x FOR THE PHONE.
			# NOTE: CHECKING MULTIPLE TIMES ISN'T NEEDED EXCEPT FOR DEBUGGING.
			# Run nmap two to three times to verify the phone is off the network.
			# Occasionally phone may not respond in time, therefore multiple checks increase accuracy.
			var = os.popen('sudo nmap -sP 192.168.1.3 | grep AA:BB:CC:DD:FF:GG').read()
			if var == "":
				var = os.popen('sudo nmap -sP 192.168.1.3 | grep AA:BB:CC:DD:FF:GG').read()
				if var == "":
					var = os.popen('sudo nmap -sP 192.168.1.3 | grep AA:BB:CC:DD:FF:GG').read()
					if var == "":
						j_away = True
						if j_away == j_away_previous:
							# Check if the current time is past the trigger time.
							if timer_20 < current_time:
								if ok_to_open == False:
									ok_to_open = True
									#print "THE TIMER IS FINISHED!"
						else:
							#print "Creating a timer. The phone has left."
							timer_20 = (datetime.datetime.now() + datetime.timedelta(minutes=20)).strftime("%H:%M:%S")
							j_away_previous = True
		# The phone is home and it's not ok to open the garage door automatically.
		elif var != "" and ok_to_open == False:
			j_away = False
			j_away_previous = False
	else:
		print "Skipping phone check while curfew is active."

# Opens/Closes Garage Door by closing relay for 0.5 seconds. Adjust as needed
def garage_toggle():
	pfd.leds[0].toggle()
	time.sleep(0.5)
	pfd.leds[0].toggle()

# Start main program and keep looping 
while True:
	current_time = (datetime.datetime.now()).strftime("%H:%M:%S")
	check_curfew()
	check_phones()
	# Reduce CPU load by including a delay. Delay can be safely removed and Pi will work find.
	# Possible downside may include increased phone battery consumption.
	if j_away == False:
		time.sleep(60)
	else:
		time.sleep(.5)
	check_open()

#	Uncomment line below for debugging.
#	time.sleep(3)
