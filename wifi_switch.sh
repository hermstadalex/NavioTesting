sudo ifconfig wlan0 down
echo -n "Brought wifi down"
sleep 5
sudo ifconfig wlan0 up
echo -n "Brought wifi back up"
sudo iwconfig wlan0 essid hot4pie key raspberry123
echo -n "Tried to connect to hot4pie"
