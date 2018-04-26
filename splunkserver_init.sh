#! /bin/bash

# For the latest, get from splunk.com
wget -O /usr/local/src/splunk-7.1.0.deb 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=7.1.0&product=splunk&filename=splunk-7.1.0-2e75b3406c5b-linux-2.6-amd64.deb&wget=true'

apt-get install -y /usr/local/src/splunk-7.1.0.deb

