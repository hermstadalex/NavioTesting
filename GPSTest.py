"""
Robotritons testing version of steering controls.
Based on iterations of the Emlid Servo.py example.

Purpose: 
Requirements:
Use: 

Resources:
https://shahriar.svbtle.com/importing-star-in-python
"""

from GPSBackEnd import *

ubl = U_blox()
#print type(ubl)
for ind in range(0, 10):
	ubl.enable_posstatus()
while(1):
	buffer = ubl.bus.xfer2([100])
	for byt in buffer:
		ubl.scan_ubx(byt)
		if(ubl.mess_queue.empty() != True):
			msg = ubl.parse_ubx()
			if (msg != None): print(msg)
