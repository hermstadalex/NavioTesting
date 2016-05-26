"""
Robotritons troubleshooting version for gps navigation.

Purpose: Use reliable GPS data to navigate the vehicle
Requirements: A vehicle with at least one speed controller and one servo, and one Ublox NEO-M8N Standard Precision GNSS Module. The python modules sys, time, GPSConfigBackEnd, and VehiclePWMModule 
Use: Instantiate esc, servo, and ublox objects then use their included methods as well as those defined here in order to wait until usable GPS data is secured.
	Instantiate objects for an esc using vehiclePWM("esc"), a servo using vehiclePWM("servo"), and a ublox using U_blox()

Resources:
https://docs.emlid.com/navio/Navio-dev/read-gps-data/
https://shahriar.svbtle.com/importing-star-in-python
"""
import sys
import time
from GPSConfigBackEnd import *
import VehiclePWMModule

#make ubl object
ubl = U_blox()

def comm(msg):
	for x in range(0,10):
		ubl.bus.xfer2(msg)

#reset the Ublox messages
CFGmsg8_NAVposllh_no = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x12,0xb9]#Disable Ublox from publishing a NAVposllh	
CFGmsg8_NAVstatus_no = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x13,0xc0]#Disable Ublox from publishing a NAVstatus
#enable the Ublox messages
CFGmsg8_NAVstatus_yes = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x01,0x00,0x14,0xc2]#Enable Ublox to publish a NAVstatus
CFGmsg8_NAVposllh_yes = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x01,0x00,0x13,0xbb]#Enable Ublox to publish a NAVposllh

vehicle_servo = VehiclePWMModule.vehiclePWM("servo")
vehicle_esc = VehiclePWMModule.vehiclePWM("esc")
#ubl.debug=True
x=1
while(True):
	try:
		if (x==1):
			vehicle_esc.stop()
			vehicle_servo.rest()
			vehicle_servo.center()
			comm(CFGmsg8_NAVstatus_no)
			comm(CFGmsg8_NAVposllh_no)
			comm(CFGmsg8_NAVstatus_yes)
			#sTime = time.time()
			a = 0
			while not(a):
				a = ubl.GPSfetch()
			print(a)
			print 'once'
			x=2
		if (x==2):
			comm(CFGmsg8_NAVstatus_no)
			vehicle_servo.steer(45)
			time.sleep(0.5)
			vehicle_servo.steer(105)
			time.sleep(0.5)
			vehicle_servo.center()
			#ubl.debug=True
			print 'twice'
			x=3
			z=1
		comm(CFGmsg8_NAVposllh_yes)
		b = 0
		while not(b):
			#vehicle_esc.accel(3)			
			b = ubl.GPSfetch(1)
			#vehicle_esc.accel(-6)
			z=z+1
		print 'z %d' % z

#I was able to reproduce the error of not getting any GPS data in the GPSBasicNav.py It has nothing to do with setting and changing CFG-Messages,
#	although if I will never get a responce before 1 second after I enable a message type. Instead it has something to do with changing speeds
#	around the ubl.GPSfetch(). Of course! I counted how long it takes the module "GPSfetch" to sucessfully find a NAVposllh message; about 1130 attempts!
#	Thus when I set accel() to different signed speeds it executes the internal time.sleeps() commands which add up to a second. In other words this use of
#	the accel() method will make each GPSfetch attempt take 1 second. I thought it was broken because it would take ~18 minutes to get a message!
#	Maybe a solution is to immediately poll for that type of message? I've added this argument to the GPSfetch() method.
#	Another solution is to start threading...
#
#	I made the fetchSpecial method to try and poll for the desired message, but no luck. It takes just as long to get a response as not polling.
#	I can't use this method right now to expedite the message receival. It looks like it will take more effort than it is worth.
#	Guess threading or ommiting time.sleep() is the only way.
#
#		if (x==8000): #Basically if we dont wait at least 1 second after Posllh is enabled, then we will not get any data
#			comm(CFGmsg8_NAVposllh_no)
#			comm(CFGmsg8_NAVstatus_yes)
#			eTime = time.time()
#			print 'elapsed %f' % (eTime-sTime)
#			print 'here'

	except KeyboardInterrupt:
		vehicle_esc.stop()
		vehicle_servo.rest()
		sys.exit()
