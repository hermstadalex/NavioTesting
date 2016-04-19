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
from Adafruit_PWM_Servo_Driver import PWM
import time
import math

import sys

sys.path.append("..")
from Navio import GPIO
# ---- End Includes ---- 

# ---- Setup Modules ----
'''
Drive LOW the Output Enable pin of the PCA9685BS model HVQFN28
The RPI2's gpio pin #27 is connected to the PCA pin "OE" #20
By driving OE LOW outputs are activated
'''
pin = GPIO.Pin(27)
pin.write(0)

'''
This assignment adresses the PCA9685BS register controlling LED14_OFF_L 
Hex constants are prefixed with "0x"
hex(0x40) = dec(64) = bin(01000000)
''' 
PCA9685_DEFAULT_ADDRESS = 0x40

frequency = 50
# ---- End Module Setup ---- 

# ---- Configure Outputs ----
'''
A digital signal controls the PCA9685 which prepares an analog PWM wave
for the Savox SC-1258TG servo.

The PCA9685 is controlled by I2C and each of the 16 drivers has 12-bit
PWM output which is 4096 steps. The analog output wave can range from
24Hz-1526Hz frequency with possible 0%-100% duty cycle.
'''
NAVIO_RCOUTPUT_1 = 3
SERVO_MIN_ms = 1.250 # mS
SERVO_MAX_ms = 1.750 # mS

#convert mS to 0-4096 scale:
SERVO_MIN = math.trunc((SERVO_MIN_ms * 4096.0) / (1000.0 / frequency) - 1)
SERVO_MAX = math.trunc((SERVO_MAX_ms * 4096.0) / (1000.0 / frequency) - 1)

pwm = PWM(0x40, debug=False)

# Set frequency to 50 Hz
pwm.setPWMFreq(frequency)
# ---- End Output Configuration ---- 

while(True):
	pwm.setPWM(NAVIO_RCOUTPUT_1, 0, SERVO_MIN);
	time.sleep(1);
	pwm.setPWM(NAVIO_RCOUTPUT_1, 0, SERVO_MAX);
	time.sleep(1);
