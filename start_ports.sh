#! /bin/bash

# Modify these as you see fit
START_PORT=6000
END_PORT=6025
INTERFACE=eth1

# Get the IP of eth1
IP=$(ifconfig ${INTERFACE} | grep "inet addr" | cut -d: -f2 | awk '{ print $1 }')

mkdir -p logs/tcp
for i in `seq ${START_PORT} ${END_PORT}`
do
	echo Starting server on port $i
	python /opt/multithreaded_socket_logger/server.py --ip ${IP} --port $i --logfile /opt/multithreaded_socket_logger/logs/tcp/$i.log --daemonize --runas nobody
done

exit 0

