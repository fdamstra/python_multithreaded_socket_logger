#!/usr/bin/python3
# A simple example of a threaded TCP server in Python.
#
# Copyright (c) 2012 Benoit Sigoure    All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright notice,
#         this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright notice,
#         this list of conditions and the following disclaimer in the documentation
#         and/or other materials provided with the distribution.
#     - Neither the name of the StumbleUpon nor the names of its contributors
#         may be used to endorse or promote products derived from this software
#         without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.    IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# --
# Original Source for a basic socket listener was https://gist.github.com/tsuna/1563257
# Modified with logging stuff by Fred Damstra
#
# Revisions:
#  2018-04-28 - Initial Revision

import socketserver
import os
import subprocess
import sys

import argparse
import logging
import threading
from threading import Thread
import _thread
import time
import pwd

def switch_to_user(user):
    if user:
        try:
            uid = pwd.getpwnam(user).pw_uid
        except KeyError:
            logging.error("User {} not found.".format(user))
            sys.exit(2)
        try:
            os.setuid(uid)
        except OSError:
            logging.error("Could not change to uid for user {}.".format(user))
            sys.exit(2)

def daemonize(user):
    if os.fork() != 0:
        os._exit(0)

    os.setsid()

    if os.fork() != 0:
        os._exit(0)

#    os.chdir("/")
#    os.umask(022)

    switch_to_user(user)
 
    [os.close(i) for i in xrange(3)]
    os.open(os.devnull, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True # Faster Binding
    daemon_threads = True # kill all connections on ctrl-c

class Handler(socketserver.StreamRequestHandler):

    def handle(self):
        start_time = time.time()
        bytecount = 0
        logging.info("action=connection_opened src_ip={} src_port={} dest_ip={} dest_port={}".format(
                    self.client_address[0],
                    self.client_address[1],
                    self.server.server_address[0],
                    self.server.server_address[1]))
        while True:
            time.sleep(1)
            command = self.rfile.readline()

            if not command:    # EOF
                end_time = time.time()
                logging.info("action=connection_closed src_ip={} src_port={} dest_ip={} dest_port={} duration={} totallength={}".format(
                    self.client_address[0],
                    self.client_address[1],
                    self.server.server_address[0],
                    self.server.server_address[1],
                    (end_time - start_time),
                    bytecount))
                break
#            self.wfile.write("your command was: %s" % (command,))
            # Sanitize and log
            currentlength = len(command)
            bytecount += currentlength
            command = command.decode("utf-8")
            command = command.replace("\"", "\\'")
            command = command.replace("\b", "\\b")
            command = command.replace("\n", "\\n")
            command = command.replace("\r", "\\r")
            logging.info('action=data_in src_ip={} src_port={} dest_ip={} dest_port={} length={} msg="{}"'.format(
                    self.client_address[0],
                    self.client_address[1],
                    self.server.server_address[0],
                    self.server.server_address[1],
                    currentlength,
                    command))

def serve_port(server, args):
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.warn("action=stopping=KeyboardInterrupt debug={} startport={} endport={} dest_ip={} protocol={} daemonize={}".format(args.debug, args.startport, args.endport, args.ip, args.protocol, args.daemonize))
        pass

def main(args):
    # Parse arguments
    parser = argparse.ArgumentParser(description='Listen on a socket and log to logfile.')
    parser.add_argument('--startport', required=True, type=int, help='Specify the first port to listen on')
    parser.add_argument('--endport', required=True, type=int, help='Specify the last port to listen on')
    parser.add_argument('--debug', action="store_true", help="Print debugging information")
    parser.add_argument('--daemonize', action="store_true", help="Run in the background.")
    parser.add_argument('--ip', default='0.0.0.0', help="Specify IP to listen on. Default is 0.0.0.0.")
    parser.add_argument('--protocol', default='tcp', choices=['tcp', 'udp'], help="Specify protocol type. UDP support experimental!")
    parser.add_argument('--logfile',    default='stdout', help="Path to logfile.")
    parser.add_argument('--runas', metavar="USERNAME", help="Run as this user.")
    args = parser.parse_args()
    if args.debug:
        print("DEBUG: Start Port: {}".format(args.startport))
        print("DEBUG: End Port: {}".format(args.endport))
        print("DEBUG: IP: {}".format(args.ip))
        print("DEBUG: Protocol: {}".format(args.protocol))
        print("DEBUG: Logfile: {}".format(args.logfile))
        print("DEBUG: Daemonize: {}".format(args.daemonize))

    if args.startport < 1 or args.startport > 65535:
        print("ERROR: Invalid start port: {}.".format(args.startport))
        sys.exit(1)

    if args.endport < 1 or args.endport > 65535:
        print("ERROR: Invalid end port: {}.".format(args.endport))
        sys.exit(1)

    if args.daemonize and (args.logfile == "stdout"):
        print("ERROR: Cannot daemonize and log to stdout.")
        sys.exit(1) 

    # Set logging
    if(args.logfile == 'stdout'):
        logging.basicConfig(level=logging.DEBUG, 
                format='%(asctime)s name=%(name)s level=%(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S %z')
    else:
        logging.basicConfig(level=logging.DEBUG, 
                format='%(asctime)s name=%(name)s level=%(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S %z',
                filename=args.logfile,
                filemode='w')
    logging.warning("action=initializing")

    servers = []
    for p in range(args.startport, args.endport+1):
        if args.protocol == 'tcp':
            try:
                servers.append(ThreadedTCPServer((args.ip, p), Handler))
            except:
                logging.error("Could not bind to port {} on ip {}".format(p, args.ip))
        else:
            print("WARNING: UDP Support is untested!")
            servers.append(ThreadedUDPServer((args.ip, p), Handler))
        logging.warn("action=started_listening debug={} dest_port={} dest_ip={} protocol={} daemonize={}".format(args.debug, p, args.ip, args.protocol, args.daemonize))

    if args.daemonize:
        if args.debug:
            print("DEBUG: Daemonizing server.")
        daemonize(args.runas)
    else:
        switch_to_user(args.runas)

    threads = []
    for s in servers:
        t = Thread( target=serve_port, args=(s, args))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    sys.exit(main(sys.argv))

