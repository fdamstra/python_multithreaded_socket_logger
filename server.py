#!/usr/bin/python
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

import SocketServer
import os
import subprocess
import sys

import argparse
import logging
import threading
import time

def daemonize():
    if os.fork() != 0:
        os._exit(0)

    os.setsid()

    if os.fork() != 0:
        os._exit(0)

    os.chdir("/")
    os.umask(022)
    [os.close(i) for i in xrange(3)]
    os.open(os.devnull, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True # Faster Binding
    daemon_threads = True # kill all connections on ctrl-c

class Handler(SocketServer.StreamRequestHandler):

    def handle(self):
        start_time = time.time()
        logging.info("action='connection opened' src_ip:{} src_port:{} dest_ip:{} dest_port:{}".format(
                    self.client_address[0],
                    self.client_address[1],
                    self.server.server_address[0],
                    self.server.server_address[1]))
        while True:
            time.sleep(1)
            command = self.rfile.readline()

            if not command:    # EOF
                end_time = time.time()
                logging.info("action='connection closed' src_ip:{} src_port:{} dest_ip:{} dest_port:{} duration:{}".format(
                    self.client_address[0],
                    self.client_address[1],
                    self.server.server_address[0],
                    self.server.server_address[1],
                    (end_time - start_time)))
                break
#            self.wfile.write("your command was: %s" % (command,))
            # Sanitize and log
            command = command.replace("'", "\\'")
            command = command.replace("\b", "\\b")
            command = command.replace("\n", "\\n")
            command = command.replace("\r", "\\r")
            logging.info("action='data in' src_ip:{} src_port:{} dest_ip:{} dest_port:{} msg='{}'".format(
                    self.client_address[0],
                    self.client_address[1],
                    self.server.server_address[0],
                    self.server.server_address[1],
                    command))

def main(args):
    # Parse arguments
    parser = argparse.ArgumentParser(description='Listen on a socket and log to logfile.')
    parser.add_argument('--port', required=True, type=int, help='Specify the port to listen on')
    parser.add_argument('--debug', action="store_true", help="Print debugging information")
    parser.add_argument('--daemonize', action="store_true", help="Run in the background.")
    parser.add_argument('--ip', default='0.0.0.0', help="Specify IP to listen on. Default is 0.0.0.0.")
    parser.add_argument('--protocol', default='tcp', choices=['tcp', 'udp'], help="Specify protocol type. UDP support experimental!")
    parser.add_argument('--logfile',    default='stdout', help="Path to logfile.")
    args = parser.parse_args()
    if args.debug:
        print "DEBUG: Port: {}".format(args.port)
        print "DEBUG: IP: {}".format(args.ip)
        print "DEBUG: Protocol: {}".format(args.protocol)
        print "DEBUG: Logfile: {}".format(args.logfile)
        print "DEBUG: Daemonize: {}".format(args.daemonize)

    if args.port < 1 or args.port > 65535:
        print "ERROR: Invalid port: {}.".format(args.port)
        sys.exit(1)

    if args.daemonize and (args.logfile == "stdout"):
        print "ERROR: Cannot daemonize and log to stdout."
        sys.exit(1) 

    if args.daemonize:
        if args.debug:
            print "DEBUG: Daemonizing server."
        daemonize()

    # Set logging
    if(args.logfile == 'stdout'):
        logging.basicConfig(level=logging.DEBUG, 
                format='%(asctime)s name=%(name)s level=%(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S.%f %z')
    else:
        logging.basicConfig(level=logging.DEBUG, 
                format='%(asctime)s name=%(name)s level=%(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S.%f %z',
                filename=args.logfile,
                filemode='w')

    logging.warn("action='started listening' debug:{} port:{} ip:{} protocol:{} daemonize:{}".format(args.debug, args.port, args.ip, args.protocol, args.daemonize))

    if args.protocol == 'tcp':
        server = ThreadedTCPServer((args.ip, args.port), Handler)
    else:
        print "WARNING: UDP Support is untested!"
        server = ThreadedUDPServer((args.ip, args.port), Handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.warn("action='Stopping: KeyboardInterrupt' debug:{} port:{} ip:{} protocol:{} daemonize:{}".format(args.debug, args.port, args.ip, args.protocol, args.daemonize))
        pass

if __name__ == "__main__":
    sys.exit(main(sys.argv))

