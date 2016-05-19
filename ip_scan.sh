sudo arp-scan -l
echo -n "Enter IP address: "
read ip
sudo APMrover2 -A udp:$ip:14550
