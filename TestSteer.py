import time
import SteerModule
vehicle_servo = SteerModule.servo()

while(True):
	vehicle_servo.rest()
	time.sleep(2)
	vehicle_servo.steer(50)
	time.sleep(2)
	vehicle_servo.steer(120)
	time.sleep(2)
	vehicle_servo.center()
	time.sleep(2)
