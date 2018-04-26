#! /bin/bash

# Make eth1 startup at boot
echo "auto eth1" > /etc/network/interfaces.d/99-eth1.cfg
echo "iface eth1 inet dhcp" >> /etc/network/interfaces.d/99-eth1.cfg

# Create rc.local to start the listener
cp /opt/multithreaded_socket_logger/start_ports.sh /etc/rc.local
chown root:root /etc/rc.local
chmod 700 /etc/rc.local

# Only listen on eth0
ifconfig eth0 | grep "inet addr" | cut -d: -f2 | awk '{ print "ListenAddress", $1 }' >> /etc/ssh/sshd_config
service sshd restart

# Grab Splunk UF
wget -O /usr/local/src/splunkforwarder-7.1.0.deb 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=7.1.0&product=universalforwarder&filename=splunkforwarder-7.1.0-2e75b3406c5b-linux-2.6-amd64.deb&wget=true'
apt-get install -y /usr/local/src/splunkforwarder-7.1.0.deb
/opt/splunkforwarder/bin/splunk enable boot-start -user splunk --accept-license --seed-passwd "NotTheDefault"
/opt/splunkforwarder/bin/splunk set deploy-server 10.66.1.10:8089 -auth admin:NotTheDefault
chown -R splunk:splunk /opt/splunkforwarder

