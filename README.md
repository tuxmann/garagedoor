garagedoor
==========

Script with webpage for controlling the garage door through the PiFace

System Requirements
===================

Raspberry Pi with Raspbian
Piface add on board or equivalent
Apache2 & PHP5 (for the door button in the browser)
toggle.py (for opening the door through the webpage)
index.php located in the /var/www/ directory for making the button

Improvemnts to the project
==========================

Pictures of what things look like
Schematics 
Improving the phone scanning feature to be called by check_open & check_phones
Reduce the complexity of the code to reduce nested if statements

Improve the webpage side so that the pi sends updated information about the
door status (open/closed/neither) and the user can lock the door open
