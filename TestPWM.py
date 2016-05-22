import time
import VehiclePWMModule
vehicle_servo = VehiclePWMModule.vehiclePWM("servo")
vehicle_esc = VehiclePWMModule.vehiclePWM("esc")

while(True):
	'''
	vehicle_esc.stop()
	time.sleep(2)
	vehicle_esc.accel(100)#Forward
	time.sleep(2)
	vehicle_esc.stop()
	time.sleep(2)
	vehicle_esc.accel(0)#First back
	time.sleep(2)
	vehicle_esc.stop()
	time.sleep(2)
	vehicle_esc.accel(0)#Actual backwards
	time.sleep(2)
	'''
	
	vehicle_esc.stop()
	vehicle_servo.rest()
	time.sleep(2)
	vehicle_servo.steer(50)
	vehicle_esc.accel(40)
	time.sleep(2)
	
	'''
	vehicle_servo.rest()
	time.sleep(2)
	vehicle_servo.steer(50)
	time.sleep(2)
	vehicle_servo.steer(120)
	time.sleep(2)
	vehicle_servo.center()
	time.sleep(2)
	'''
