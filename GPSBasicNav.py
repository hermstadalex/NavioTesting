"""
Robotritons testing version of gps navigation.

Purpose: Use reliable GPS data to navigate the vehicle
Requirements: A vehicle with at least one speed controller and one servo, and one Ublox NEO-M8N Standard Precision GNSS Module. The python modules sys, time, VehicleGPSModule, and VehiclePWMModule 
Use: Instantiate esc, servo, and ublox objects then use their included methods as well as those defined here in order to wait until usable GPS data is secured.
	Instantiate objects for an esc using vehiclePWM("esc"), a servo using vehiclePWM("servo"), and a ublox using U_blox()

Updates:
- May 26, 2016. I was finally able to reproduce the error of GPSfetch not returning a message. It has nothing to do with rapidly setting and changing CFG-Messages,
	(although 1 second mus pass after a message is enabled/disabled) but instead is caused when accel() changes direction inside the GPSfetch loop. When two back-back
	accel() statements have different signed speeds then the internal time.sleep() is executed for a total of 1 second. In other words each GPSfetch attempt will occur
	with a period of 1 second. But GPSfetch requires many, many, attempts to sucessfully find a NAVposllh message, about 1130 attempts by my count, so it would take
	~18 minutes for GPSfix to work running at one execution/second.
	
	Maybe a solution is to immediately poll for that type of message? I made the fetchSpecial method to poll for the desired message and expedite the message receival.
	But no luck: it takes just as long to get a response as not polling. Looks like it will take more effort than it is worth.
	I Guess threading or ommiting time.sleep() is the only solution.

- May 25, 2016. Found accel() execution of time.sleep() as the SOURCE OF ERROR causing GPSfetch() to never get a valid message. The pauses in
	the accel commands cannot be run with the nav message updates because it will take ~1000 tries to get a message. Also, noticed a POTENTIAL ERROR
	that accel statements move the vehicle only as long as the pwm generator maintains the same state. Aka, changing accel states too quickly
	means that output won't transfer to vehicle motion. Either structure your accel statements well, or they need to be made into a threaded process.
- May 24, 2016. The VehicleGPSModule methods NavStatusMessage and Parse_ubx naturally return values in addition to text. I made GPSfetch to capitolize
	on this behavior. GPSfetch packages the repetative set of commands to buffer and check message for data from the Ublox. Also I fixed accel from
	entering an infinite loop; now calling accel() multiple times and passing different signed arguments works.

Resources:
https://docs.emlid.com/navio/Navio-dev/read-gps-data/
https://shahriar.svbtle.com/importing-star-in-python
"""
import sys
import time
from VehicleGPSModule import *
import VehiclePWMModule

ubl = U_blox()
'''
mess_CFG_PRT_IO = [0xb5,0x62,0x06,0x00,0x01,0x00,0x04,0x0b,0x25]
mess_CFG_MSG1 = [0xb5,0x62,0x06,0x01,0x02,0x00,0x01,0x02,0x0c,0x35]#this is for a NavPosllh
mess_CFG_MSG2 = [0xb5,0x62,0x06,0x01,0x02,0x00,0x01,0x03,0x0d,0x36]#this is for a NavStatus
mess_CFG_MSG8D = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x12,0xb9]#this is to disable a NavPosllh
mess_CFG_MSG8E = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x01,0x00,0x13,0xbb]#this is to re-enable a NavPosllh
messGet_CFG_PRT_SPI = [0xb5,0x62,0x06,0x00,0x14,0x00,0x04, "19more","chka","chkb"]
'''
#reset the Ublox messages
CFGmsg8_NAVposllh_no = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x12,0xb9]#Disable Ublox from publishing a NAVposllh	
CFGmsg8_NAVstatus_no = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x13,0xc0]#Disable Ublox from publishing a NAVstatus
#enable the Ublox messages
CFGmsg8_NAVstatus_yes = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x01,0x00,0x14,0xc2]#Enable Ublox to publish a NAVstatus
CFGmsg8_NAVposllh_yes = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x01,0x00,0x13,0xbb]#Enable Ublox to publish a NAVposllh

def comm(msg):
	for x in range(0,10):
		ubl.bus.xfer2(msg)

def GPSNavInit():

	#reset the Ublox messages
	for x in range(0, 10):
		ubl.bus.xfer2(CFGmsg8_NAVposllh_no)
		ubl.bus.xfer2(CFGmsg8_NAVstatus_no)
	print 'all NAV stopped'

	#Enable the gps status messages
	for x in range(0, 10):
		ubl.bus.xfer2(CFGmsg8_NAVstatus_yes)
	print 'NAVstatus started'

	#Wait until we have a confirmed GPS fix
	goodGPSfix = True
	while not (goodGPSfix):
		GPSfix = ubl.GPSfetch()
		if (GPSfix):
			if((GPSfix['fStatus'] == 2) or (GPSfix['fStatus'] == 3) or (GPSfix['fStatus'] == 4)):
				goodGPSfix = True
	print 'goodFix \n'

	#After confirmed fix, disable Navstatus messages
	for x in range(0, 10):
		ubl.bus.xfer2(CFGmsg8_NAVstatus_no)
		
	#Wiggle weels to indicate done init
	vehicle_servo.steer(45)
	time.sleep(0.5)
	vehicle_servo.steer(105)
	time.sleep(0.5)
	vehicle_servo.center()

def NAVposllhUpdate():
	#Start the NAVposllh messages
	for x in range(0,10):
		ubl.bus.xfer2(CFGmsg8_NAVposllh_yes)
	##msg = [0xb5, 0x62, 0x06, 0x01, 0x03, 0x00, 0x01, 0x02, 0x01, 0x0e, 0x47]

	#Move forward and back slowly until established valuable horizontal accuraccy
	#print 'starting gps acc'
	#ubl.debug=True
	goodGPSacc = False
	while not (goodGPSacc):
		vehicle_esc.accel(1) #Move forward a little since it wasn't accurate
		time.sleep(1)
		vehicle_esc.stop()
		#s = time.time()
		#e = time.time()
		while((e-s) < 1):
			acc = ubl.GPSfetch()
			if (acc):
				if (acc['hAcc'] <= 200000):#change to 10 for actual testing
					goodGPSacc = True
			e = time.time()
		#print 'passed'
		vehicle_esc.accel(-5) #Move backward to our original position
		time.sleep(1)
		vehicle_esc.stop()
	print 'good acc \n'

	#Stop shennanigans now that we've got an accurate gps readings
	vehicle_esc.stop()
	
	#Grab the current gps location
	pos = ubl.GPSfetch()	
	print pos, '\n'
	#Know next location
	#calculate next waypoint heading
	#Set course to move towards next waypoint



vehicle_servo = VehiclePWMModule.vehiclePWM("servo")
vehicle_esc = VehiclePWMModule.vehiclePWM("esc")
x = 1

while(True):
	try:
		vehicle_esc.stop()
		vehicle_esc.rest()
		vehicle_servo.center()
		if (x==1): 	#Don't run GPSNavInit a second time when NavPosllh messages are enabled because GPSNavInit expects a NavStatus dictionary with the key "fStatus"
			GPSNavInit()
			x=2
		NAVposllhUpdate()

	except KeyboardInterrupt:
		vehicle_esc.stop()
		vehicle_servo.rest()
		sys.exit()

