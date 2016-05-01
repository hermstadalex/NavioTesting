"""
Robotritons testing version of steering controls.
Based on iterations of the Emlid Servo.py example.

Purpose: Steer the vehicle by sending PWM signals to the Savox SC-1258TG Servo
Requirements: Adafruit I2C and PCA9685 PWM generator drivers
Use: Connect the Savox Servo to the Navio+ servo rail then run "sudo python SteeringWrapper.py"

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
Enable PWM outputs.
Drive the PCA9685BS model HVQFN28's OE pin #20 (27 RPI2) to "LOW"
'''
pin = navio.gpio.Pin(27)
pin.write(0)

'''
Adresses the PCA9685BS register controlling LED14_OFF_L 
''' 
PCA9685_DEFAULT_ADDRESS = 0x40
frequency = 300 #Please use frequencies 50Hz OR 300Hz for this code to reliably operate the steering servo.
#Other intermittent frequencies like 60,90,100 may or may not work. There doesn't appear to be a pattern.
period = 1.0/frequency

NAVIO_RCOUTPUT_1 = 3
# ---- End Module Setup ---- 

# ---- Set & Convert Outputs ----
'''
A 12bit digital I2C signal controls the PCA9685 which then prepares an
analog PWM wave for the Savox SC-1258TG servo.
The PWM signal's absolute width directly controls the servo's angle.
Emperical testing on April 4, 2016 shows that in order to maintain a
constant signal width, the value of the 12 bits written must change
with respect to the operating frequency. The specific relation:

	12BitWritten = 12BitRange * (DesiredSignalWidth * OperatingFrequency)
'''
PWM_MinWidth = 0.000685 #S. This calculation was updated on April 30, 2016. It is made large enough to work at 300Hz
PWM_MaxWidth = 0.002675 #S. This calculation was updated on April 30, 2016. It is made small enough to work at 50Hz
PWM_Range = PWM_MaxWidth - PWM_MinWidth #0.00199
SERVO_rest = 0 #S. To rest servo so it doesn't hold a position, send an invalid PWM signal by sending an invalid 0-4096 bits.

# Define servo degrees of movement
SERVO_Range = 180.0 #This must be a float for correct calculations/operation

# Set desired steering positions, 
SERVO_deg1 = 50 #50 to turn full right
SERVO_deg2 = 120 #120 is turn full left
SERVO_degCenter = 85 #95 to center

# Convert our 180 degree positions to PWM widths in seconds
PWM_Width1 = PWM_MinWidth + (PWM_Range * (SERVO_deg1/SERVO_Range))
PWM_Width2 = PWM_MinWidth + (PWM_Range * (SERVO_deg2/SERVO_Range))
PWM_WidthCenter = PWM_MinWidth + (PWM_Range * (SERVO_degCenter/SERVO_Range))

#Convert PWM widths to 12 bits (a scale of 0-4095) to write to the PCA9685.
SERVO_move1 = math.trunc((4096.0 * PWM_Width1 * frequency) -1)
SERVO_move2 = math.trunc((4096.0 * PWM_Width2 * frequency) -1)
SERVO_moveCenter = math.trunc((4096.0 * PWM_WidthCenter * frequency) -1)

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
		pwm.setPWM(NAVIO_RCOUTPUT_1, 0, SERVO_moveCenter);
		time.sleep(1);
		pwm.setPWM(NAVIO_RCOUTPUT_1, 0, SERVO_rest);
		time.sleep(3);
	except KeyboardInterrupt:
		sys.exit()
