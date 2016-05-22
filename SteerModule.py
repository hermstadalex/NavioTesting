"""
Robotritons steering definition and initialization module.
Based on the Emlid Servo.py example.

Purpose: Manage the PCA9685 to generate PWM signals output to the Savox SC-1258TG Servo.
Requirements: Adafruit I2C and PCA9685 PWM generator drivers.
Use: Connect the Savox Servo to the Navio+ servo rail. Include this module in any python script. Create an object from the "steer" class. Control it using the available methods.
Updates:
- May 21, 2016 all methods now respond to keyboard interrupts by relaxing the servo!

Resources:
PCA9685 Datasheet= http://www.nxp.com/documents/data_sheet/PCA9685.pdf
PCA9685 Emlid Explanation= http://docs.emlid.com/navio/Navio-dev/servo-and-rgb-led/
RPI2 <-> PCA9685 Pinout= https://community.emlid.com/t/electronic-schematics-and-mechanical-dimensions/174
Two descriptions of linux system GPIO interface
=http://falsinsoft.blogspot.com/2012/11/access-gpio-from-linux-user-space.html
=http://elinux.org/RPi_GPIO_Code_Samples#sysfs
"""
# ---- Includes ---- 
from navio.adafruit_pwm_servo_driver import PWM
import math

import sys
import signal

import navio.gpio
import navio.util

navio.util.check_apm()
# ---- End Includes ---- 

class servo:
	def __init__(self):
# ---- Setup PWM Generator ----
		self.pin = navio.gpio.Pin(27)#Enable PWM outputs.
		self.pin.write(0)#Drive the PCA9685BS model HVQFN28's OE pin #20 (27 RPI2) to "LOW"

		self.PCA9685_DEFAULT_ADDRESS = 0x40#Adresses the PCA9685BS register controlling LED14_OFF_L 
		self.frequency = 300
		#Please use frequencies 50Hz OR 300Hz for this code to reliably operate the steering servo.
		#Other intermittent frequencies like 60,90,100 may or may not work. There doesn't appear to be a pattern.
		self.period = 1.0/self.frequency
		self.NAVIO_RCOUTPUT = 3

		self.pwm = PWM(0x40, debug=False)#Set PWM register address.
		self.pwm.setPWMFreq(self.frequency)#Set output pulse frequency of the PCA9685.
		self.rest()
# ---- End PWM Generator Setup ---- 
# ---- Set Output Constants ----
		'''
A 12bit digital I2C signal controls the PCA9685 which then prepares an
analog PWM wave for the Savox SC-1258TG servo.
The PWM signal's absolute width directly controls the servo's angle.
Emperical testing on April 4, 2016 shows that in order to maintain a
constant signal width, the value of the 12 bits written must change
with respect to the operating frequency. The specific relation:

	12BitWritten = 12BitRange * (DesiredSignalWidth * OperatingFrequency)
		'''
		self.PWM_MinWidth = 0.000685 #S. This calculation was updated on April 30, 2016. It is made large enough to work at 300Hz
		self.PWM_MaxWidth = 0.002675 #S. This calculation was updated on April 30, 2016. It is made small enough to work at 50Hz
		self.PWM_Range = self.PWM_MaxWidth - self.PWM_MinWidth #0.00199
		self.SERVO_Range = 180.0 #Define servo degrees of movement. Must be a float for correct calculations/operation
# ---- End Output Constants ----

	def steer(self, deg):
# ---- Convert Outputs ----
		#deg = 50 to turn full right
		#deg = 120 to turn full left
		#deg = 85/95 to center
		PWM_Width = self.PWM_MinWidth + (self.PWM_Range * (deg/self.SERVO_Range))# Convert our 180 degree positions to PWM widths in seconds
		SERVO_move = math.trunc((4096.0 * PWM_Width * self.frequency) -1)#Convert PWM widths to 12 bits (a scale of 0-4095) to write to the PCA9685.
# ---- End Convert Outputs ----
		try:
			self.pwm.setPWM(self.NAVIO_RCOUTPUT, 0, SERVO_move)
		except KeyboardInterrupt:
			self.rest()
			sys.exit()

	def center(self):
		PWM_Width = self.PWM_MinWidth + (self.PWM_Range * (75/self.SERVO_Range))		
		SERVO_move = math.trunc((4096.0 * PWM_Width * self.frequency) -1)
		try:
			self.pwm.setPWM(self.NAVIO_RCOUTPUT, 0, SERVO_move)
		except KeyboardInterrupt:
			self.rest()
			sys.exit()
	def rest(self):
		self.pwm.setPWM(self.NAVIO_RCOUTPUT, 0, 0)#0S. To rest servo so it doesn't hold a position, send an invalid PWM signal by sending an invalid 0-4096 bits.
