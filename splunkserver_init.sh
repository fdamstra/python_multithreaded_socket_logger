#! /bin/bash

# For the latest, get from splunk.com
wget -O /usr/local/src/splunk-7.1.0.deb 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=7.1.0&product=splunk&filename=splunk-7.1.0-2e75b3406c5b-linux-2.6-amd64.deb&wget=true'
apt-get install -y /usr/local/src/splunk-7.1.0.deb
sudo -u splunk /opt/splunk/bin/splunk start --accept-license --seed-passwd "NotTheDefault"
/opt/splunk/bin/splunk enable boot-start -user splunk
/opt/splunk/bin/splunk enable deploy-server -auth admin:NotTheDefault
/opt/splunk/bin/splunk enable web-ssl -auth admin:NotTheDefault
/opt/splunk/bin/splunk stop

# Install honeypot app
cp -r /opt/multithreaded_socket_logger/splunk_config/apps/honeypot_inputs/ /opt/splunk/etc/deployment-apps/
cp -r /opt/multithreaded_socket_logger/splunk_config/apps/honeypot_outputs/ /opt/splunk/etc/deployment-apps/
cp /opt/multithreaded_socket_logger/splunk_config/serverclass.conf /opt/splunk/etc/system/local/
cp /opt/multithreaded_socket_logger/splunk_config/inputs.conf.splunk-hp /opt/splunk/etc/system/local/inputs.conf

# Fix any perms
chown -R splunk:splunk /opt/splunk

# Redirect 443 to spunk
iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 8000
service netfilter-persistent start
invoke-rc.d netfilter-persistent save
netfilter-persistent save

# System will reboot
