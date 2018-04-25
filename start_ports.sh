#! /bin/bash

# Modify these as you see fit
START_PORT=6000
END_PORT=6025

mkdir -p logs/tcp
for i in `seq ${START_PORT} ${END_PORT}`
do
	echo Starting server on port $i
	python server.py --port $i --logfile logs/tcp/$i.log --daemonize --runas nobody
done

exit 0

