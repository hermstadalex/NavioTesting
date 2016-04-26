"""
Robotritons testing of the Xerun SCT-Pro ESC

Purpose: Control the ESC that powers the motor
Requirements: Adafruit I2C and PCA9685 PWM generator drivers
Use: Connect a PWM input device to the Navio+ servo rail then run "sudo python EscWrapper.py"

Resources:
http://www.societyofrobots.com/robotforum/index.php?topic=4299.0
http://robots.dacloughb.com/project-2/esc-calibration-programming/ (edited)
http://aeroquad.com/showthread.php?5502-Which-PWM-frequency-do-I-use-to-control-my-ESC (edited)
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
By driving Output Enable LOW outputs are activated
'''
pin = navio.gpio.Pin(27)
pin.write(0)

'''
Adresses the PCA9685BS register controlling LED14_OFF_L 
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
'''
PWM_MinWidth = 0.000675 #S. This was calculated on April 4, 2016
#PWM_NeutWidth = 0.0015 #S. This is informed from part documentation
PWM_MaxWidth = 0.002425 #S. This is a guess
PWM_Range = PWM_MaxWidth - PWM_MinWidth #0.00175

# Define motor max speed
Motor_Range = 180

# Set desired motor speeds
Motor_speed1 = 0
Motor_speed2 = 100

# Convert our 180 degree positions to PWM widths in seconds
PWM_Width1 = PWM_MinWidth + (PWM_Range * (Motor_deg1/Motor_Range))
PWM_Width2 = PWM_MinWidth + (PWM_Range * (Motor_deg2/Motor_Range))
#WM_Width1 = PWM_MaxWidth - (PWM_Range * (1 - (SERVO_deg1/SERVO_Range))) #This is a messy alternative to the line above
#PWM_Width2 = PWM_MaxWidth - (PWM_Range * (1 - (SERVO_deg2/SERVO_Range)))

#Convert PWM widths to 12 bits (a scale of 0-4095) to write to the PCA9685.
Motor_move1 = math.trunc((4096.0 * PWM_Width1 * frequency) -1)
Motor_move2 = math.trunc((4096.0 * PWM_Width2 * frequency) -1)

# Set PWM register address
pwm = PWM(0x40, debug=False)

# Set output pulse frequency of the PCA9685
pwm.setPWMFreq(frequency)

# ---- End Set & Convert Outputs ----

while(True):
	try:
		pwm.setPWM(NAVIO_RCOUTPUT_1, 0, Motor_move1);
		time.sleep(1);
		pwm.setPWM(NAVIO_RCOUTPUT_1, 0, Motor_move2);
		time.sleep(1);
	except KeyboardInterrupt:
		sys.exit()
