"""
Robotritons testing of the Xerun SCT-Pro ESC

Purpose: Control the ESC that powers the motor
Requirements: Adafruit I2C and PCA9685 PWM generator drivers
Use: Connect the Xerun ESC to the Navio+ servo rail then run "sudo python EscWrapper.py"

Resources:
http://www.societyofrobots.com/robotforum/index.php?topic=4299.0
http://robots.dacloughb.com/project-2/esc-calibration-programming/ (edited)
http://aeroquad.com/showthread.php?5502-Which-PWM-frequency-do-I-use-to-control-my-ESC (edited)
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
frequency = 45.05 #45.04 is 49.80Hz and 45.05 is above 50.15Hz
period = 1.0/frequency

NAVIO_RCOUTPUT_3 = 5
# ---- End Module Setup ---- 

# ---- Set & Convert Outputs ----
'''
A 12 bit digital I2C signal controls the PCA9685 which then prepares an
analog PWM wave for the Xerun SCT-Pro ESC.
The PWM signal's absolute width directly controls the motor speed.
Emperical testing on April 4, 2016 shows that in order to maintain a
constant signal width, the value of the 12 bits written must change
with respect to the operating frequency. The specific relation:

	12BitWritten = 12BitRange * (DesiredSignalWidth * OperatingFrequency)
'''
PWM_MinWidth = 0.001158 #S. This was measured on May 1, 2016.
PWM_MaxWidth = 0.001914 #S. This was measured on May 1, 2016.
PWM_Range = PWM_MaxWidth - PWM_MinWidth #0.000756
PWM_stop = 0.001534 #S. To stop the motor, send a constant stop pulse.

# Define motor max speed
Motor_Range = 100.0

# Set desired motor speeds
Motor_speed1 = 0
Motor_speed2 = 100

# Convert our 180 degree positions to PWM widths in seconds
PWM_Width1 = PWM_stop + (PWM_Range * (Motor_speed1/Motor_Range))
PWM_Width2 = PWM_stop + (PWM_Range * (Motor_speed2/Motor_Range))

#Convert PWM widths to 12 bits (a scale of 0-4095) to write to the PCA9685.
Motor_move1 = math.trunc((4096.0 * 0.0021 * frequency) -1) #Changed this on May 2, 2016 to get about 1.91ms output
Motor_move2 = math.trunc((4096.0 * PWM_Width2 * frequency) -1)
print Motor_move1

# Set PWM register address
pwm = PWM(0x40, debug=False)

# Set output pulse frequency of the PCA9685
pwm.setPWMFreq(frequency)

# ---- End Set & Convert Outputs ----


# Below at T = 0.0017 is the neutral, corresponding to about 1.5ms
# Need to change code below to some sort of initialization sequence:
Motor_move_start = math.trunc((4096.0 * 0.001700 * frequency) -1)
Motor_move_start2 = math.trunc((4096.0 * 0.001750 * frequency) -1)
Motor_move_start3 = math.trunc((4096.0 * 0.001550 * frequency) -1)

#pwm.setPWM(NAVIO_RCOUTPUT_3, 0, Motor_move_start);
#time.sleep(10);
# End of initialization sequence

while(True):
	try:
		pwm.setPWM(NAVIO_RCOUTPUT_3, 0, Motor_move_start);
		time.sleep(2);
		pwm.setPWM(NAVIO_RCOUTPUT_3, 0, Motor_move_start2);
		time.sleep(2);
                pwm.setPWM(NAVIO_RCOUTPUT_3, 0, Motor_move_start);
                time.sleep(2);
		pwm.setPWM(NAVIO_RCOUTPUT_3, 0, Motor_move_start3);
                time.sleep(2);
                pwm.setPWM(NAVIO_RCOUTPUT_3, 0, Motor_move_start);
                time.sleep(2);
                pwm.setPWM(NAVIO_RCOUTPUT_3, 0, Motor_move_start3);
                time.sleep(2);
		#pwm.setPWM(NAVIO_RCOUTPUT_3, 0, Motor_move2);
		#time.sleep(5);
	except KeyboardInterrupt:
		sys.exit()
