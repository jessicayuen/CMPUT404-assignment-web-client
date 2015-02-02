#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Copyright 2015 Jessica Yuen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import urllib
import urlparse

def help():
    print 'httpclient.py [GET/POST] [URL]\n'

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self, url):
        parsed_url = urlparse.urlparse(url)
        host = parsed_url.hostname
        if parsed_url.port == None:
            port = 80
        else:
            port = parsed_url.port
        return [host, port]

    def connect(self, host, port):
        return socket.create_connection((host, port), 5)

    def get_code(self, data):
        return int(data.split()[1])

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        host, port = self.get_host_port(url)
        sock = self.connect(host, port)
        parsed_url = urlparse.urlparse(url)
        request =  'GET %s HTTP/1.1\r\n' % parsed_url.path
        request += 'Host: %s\r\n' % parsed_url.netloc
        if args != None:
            request += '%s\r\n' % urllib.urlencode(args)
        request += 'Connection: close\r\n\r\n'
        sock.sendall(request);
        data = self.recvall(sock)
        return HTTPRequest(self.get_code(data), self.get_body(data))

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        sock = self.connect(host, port)
        parsed_url = urlparse.urlparse(url)
        content = ''
        if args != None:
            content = urllib.urlencode(args)
        request =  'POST %s HTTP/1.1\r\n' % parsed_url.path
        request += 'Host: %s\r\n' % parsed_url.netloc
        request += 'Content-Length: %d\r\n' % len(content)
        request += 'Content-Type: application/x-www-form-urlencoded\r\n'
        request += 'Connection: close\r\n\r\n'
        request += content
        sock.sendall(request)
        data = self.recvall(sock)
        return HTTPRequest(self.get_code(data), self.get_body(data))

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

if __name__ == "__main__":
    client = HTTPClient()
    command = 'GET'
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )
