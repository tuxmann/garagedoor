import pifacedigitalio
import time

# Create & Init a PiFace Digtal object
pfd = pifacedigitalio.PiFaceDigital()

# Close relay 0 for 0.5 seconds
pfd.leds[0].toggle()
time.sleep(0.5)
pfd.leds[0].toggle()
