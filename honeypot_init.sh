#! /bin/bash

# Make eth1 startup at boot and route correctly
echo 200 honeypot >> /etc/iproute2/rt_tables
echo "auto eth1" > /etc/network/interfaces.d/99-eth1.cfg
echo "iface eth1 inet static" >> /etc/network/interfaces.d/99-eth1.cfg
echo "address 10.66.0.10" >> /etc/network/interfaces.d/99-eth1.cfg
echo "netmask 255.255.255.0" >> /etc/network/interfaces.d/99-eth1.cfg
echo "up ip rule add from 10.66.0.10 table honeypot" >> /etc/network/interfaces.d/99-eth1.cfg
echo "up ip route add default via 10.66.0.1 dev eth1 table honeypot" >> /etc/network/interfaces.d/99-eth1.cfg

# Create rc.local to start the listener
cp /opt/multithreaded_socket_logger/system_config/rc.local /etc/rc.local
chown root:root /etc/rc.local
chmod 700 /etc/rc.local

# Disable source verification
cp /opt/multithreaded_socket_logger/system_config/10-network-security.conf /etc/sysctl.d/10-network-security.conf

# Only listen on eth0
ifconfig eth0 | grep "inet addr" | cut -d: -f2 | awk '{ print "ListenAddress", $1 }' >> /etc/ssh/sshd_config
service sshd restart

# Grab Splunk UF
wget -O /usr/local/src/splunkforwarder-7.1.0.deb 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=7.1.0&product=universalforwarder&filename=splunkforwarder-7.1.0-2e75b3406c5b-linux-2.6-amd64.deb&wget=true'
apt-get install -y /usr/local/src/splunkforwarder-7.1.0.deb
/opt/splunkforwarder/bin/splunk enable boot-start -user splunk --accept-license --seed-passwd "NotTheDefault"
/opt/splunkforwarder/bin/splunk set deploy-poll 10.66.1.10:8089 -auth admin:NotTheDefault
echo "SPLUNK_BINDIP=127.0.0.1" >> /opt/splunkforwarder/etc/splunk-launch.conf
chown -R splunk:splunk /opt/splunkforwarder

