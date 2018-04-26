#! /bin/bash

# Make eth1 startup at boot
echo "auto eth1" > /etc/network/interfaces.d/99-eth1.cfg
echo "iface eth1 inet dhcp" >> /etc/network/interfaces.d/99-eth1.cfg

# Create rc.local to start the listener
cp /opt/multithreaded_socket_logger/start_ports.sh /etc/rc.local
chown root:root /etc/rc.local
chmod 700 /etc/rc.local

# Only listen on eth0
#ifconfig eth0 | grep "inet addr" | cut -d: -f2 | awk '{ print "ListenAddress", $1 }' >> /etc/ssh/sshd_config
#service sshd restart

