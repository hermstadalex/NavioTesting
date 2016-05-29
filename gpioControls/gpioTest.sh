#!/bin/bash
 
# monitor GPIO pin 31 (wiringPi pin 1) for shutdown signal
 
# export GPIO pin 31 and set to input with pull-up
echo "12" > /sys/class/gpio/unexport
