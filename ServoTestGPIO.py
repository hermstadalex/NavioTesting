"""
Robotritons testing version of Emlid Servo.py example

Purpose: Control the Servo machines connected to PCA9685 driver onboard of Navio shield for Raspberry Pi
Requirements: Adafruit I2C and PCA9685 PWM generator drivers
Use: Connect a PWM input device to the Navio+ servo rail then run "sudo python Servo1.py"
"""
# ---- Includes ---- 
from Adafruit_PWM_Servo_Driver import PWM
import time
import math

import sys

sys.path.append("..")
from Navio import GPIO
# ---- End Includes ---- 

# ---- Setup Modules ---- 
#drive Output Enable in PCA low
pin = GPIO.Pin(27)
pin.write(0)

PCA9685_DEFAULT_ADDRESS = 0x40
frequency = 50
# ---- End Module Setup ---- 

# ---- Configure Outputs ---- 
NAVIO_RCOUTPUT_1 = 3
SERVO_MIN_ms = 1.250 # mS
SERVO_MAX_ms = 1.750 # mS

#convert mS to 0-4096 scale:
SERVO_MIN = math.trunc((SERVO_MIN_ms * 4096.0) / (1000.0 / frequency) - 1)
SERVO_MAX = math.trunc((SERVO_MAX_ms * 4096.0) / (1000.0 / frequency) - 1)

pwm = PWM(0x40, debug=False)

# Set frequency to 60 Hz
pwm.setPWMFreq(frequency)
# ---- End Output Configuration ---- 

while(True):
	pwm.setPWM(NAVIO_RCOUTPUT_1, 0, SERVO_MIN);
	time.sleep(1);
	pwm.setPWM(NAVIO_RCOUTPUT_1, 0, SERVO_MAX);
	time.sleep(1);
