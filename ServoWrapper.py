"""
Robotritons testing version of Emlid Servo.py example

Purpose: Control the Servo machines connected to PCA9685BS ic onboard of Navio shield for Raspberry Pi
Requirements: Adafruit I2C and PCA9685 PWM generator drivers
Use: Connect a PWM input device to the Navio+ servo rail then run "sudo python Servo1.py"

Resources:
PCA9685 Datasheet= http://www.nxp.com/documents/data_sheet/PCA9685.pdf
PCA9685 Emlid Explanation= http://docs.emlid.com/navio/Navio-dev/servo-and-rgb-led/
RPI2 <-> PCA9685 Pinout= https://community.emlid.com/t/electronic-schematics-and-mechanical-dimensions/174
Two descriptions of linux system GPIO interface
=http://falsinsoft.blogspot.com/2012/11/access-gpio-from-linux-user-space.html
=http://elinux.org/RPi_GPIO_Code_Samples#sysfs
"""
# ---- Includes ---- 
from navio.adafruit_PWM_servo_driver import PWM
import time
import math

import sys
import signal

import navio.gpio
import navio.util

navio.util.check_apm()
# ---- End Includes ---- 

# ---- Setup Modules ----
'''
Drive LOW the Output Enable pin of the PCA9685BS model HVQFN28
The RPI2's gpio pin #27 is connected to the PCA pin "OE" #20
By driving OE LOW outputs are activated
'''
pin = navio.gpio.Pin(27)
pin.write(0)

'''
This assignment adresses the PCA9685BS register controlling LED14_OFF_L 
Hex constants are prefixed with "0x"
hex(0x40) = dec(64) = bin(01000000)

Also the PCA9685 analog output wave can range from 24Hz-1526Hz frequency
and the Savox Servo likes to receive PWM frequencies of 255H0-330Hz.
''' 
PCA9685_DEFAULT_ADDRESS = 0x40
frequency = 300
period = 1.0/frequency

NAVIO_RCOUTPUT_1 = 3
# ---- End Module Setup ---- 

# ---- Set & Convert Outputs ----
'''
A digital signal controls the PCA9685 which prepares an analog PWM wave
for the Savox SC-1258TG servo.

The PCA9685 is controlled by writing 12bits over I2C to one of the 16
 output drivers. These 12 bits control the generated output pulse width.
 The signal's absolute width, not its duty cycle, directly controls the
 servo's angle.
Emperical testing on April 4, 2016 shows that in order to maintain a
 a constant signal width, the value of the 12 bits written must change
 with respect to the operating frequency. The specific relation:

		12BitWritten = 12BitRange * (DesiredSignalWidth * OperatingFrequency)

 Notice the ratio of the PWM width to the operating frequency, it is
 used to scale the total bit range.
 Example 1) Output minimum PWM width that moves (cw direction) the servo
 
		SERVO_moveMin = math.trunc ((MinWidth*frequency*4096.0)-1)
		
 Example 2) Output maximum PWM width that moves (ccw direction) the servo
 
		SERVO_moveMin = math.trunc ((MaxWidth*frequency*4096.0)-1)

'''
PWM_MinWidth = 0.000675 #S. This was calculated on April 4, 2016
#PWM_NeutWidth = 0.0015 #S. This is informed from part documentation
PWM_MaxWidth = 0.002425 #S. This is a guess
PWM_Range = PWM_MaxWidth - PWM_MinWidth #0.00175

# Define servo degrees of movement
SERVO_Range = 180

# Set desired servo positions
SERVO_deg1 = 0
SERVO_deg2 = 180

# Convert our 180 degree positions to PWM widths in seconds
PWM_Width1 = PWM_MinWidth + (PWM_Range * (SERVO_deg1/SERVO_Range))
PWM_Width2 = PWM_MinWidth + (PWM_Range * (SERVO_deg2/SERVO_Range))
#WM_Width1 = PWM_MaxWidth - (PWM_Range * (1 - (SERVO_deg1/SERVO_Range))) #This is a messy alternative to the line above
#PWM_Width2 = PWM_MaxWidth - (PWM_Range * (1 - (SERVO_deg2/SERVO_Range)))

#Convert PWM widths to 12 bits (a scale of 0-4095) to write to the PCA9685.
SERVO_move1 = math.trunc((4096.0 * PWM_Width1 * frequency) -1)
SERVO_move2 = math.trunc((4096.0 * PWM_Width2 * frequency) -1)

# Set PWM register address
pwm = PWM(0x40, debug=False)

# Set output pulse frequency of the PCA9685
pwm.setPWMFreq(frequency)

# ---- End Set & Convert Outputs ----

while(True):
	try:
		pwm.setPWM(NAVIO_RCOUTPUT_1, 0, SERVO_move1);
		time.sleep(1);
		pwm.setPWM(NAVIO_RCOUTPUT_1, 0, SERVO_move2);
		time.sleep(1);
	except KeyboardInterrupt:
		sys.exit()
