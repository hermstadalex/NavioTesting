{
sudo ifconfig wlan0 down
echo -n "Brought wifi down"
sleep 5
sudo iwconfig wlan0 essid hot4pie key raspberry123
echo -n "Tried to connect to hot4pie"
sudo ifconfig wlan0 up essid hot4pie key raspberry123
echo -n "Brought wifi back up trying again to connect to hot4pie"
} >> wifi_switch_out.txt 2>&1
