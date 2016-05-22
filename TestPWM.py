import time
import VehiclePWMModule
vehicle_servo = VehiclePWMModule.vehiclePWM("servo")
vehicle_esc = VehiclePWMModule.vehiclePWM("esc")


while(True):
	
	vehicle_esc.stop()
	time.sleep(2)
	vehicle_esc.accel(1)#Forward
	time.sleep(2)
	vehicle_esc.accel(-10)
	time.sleep(2)
	
