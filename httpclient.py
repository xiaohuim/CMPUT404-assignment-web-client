#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Xiaohui Ma
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
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        #p = re.compile(r'^(https?://|)(?P<host>[^:/]+)(:(?P<port>\d+)|)(?P<path>(/.*|))$')
        p = re.compile(r'^(https?://|)(?P<host>[^:/]+):?(?P<port>\d+?|)(?P<path>(/.*?|))(\?.*|)$')
        m = p.match(url)
        if m:
            host = m.group('host')
            port = int(m.group('port')) if m.group('port') else 80
            path = m.group('path') if m.group('path') else '/'
        else:
            print("[Error] error parsing the url!")
        return (host, port, path)

    def connect(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        return None

    def get_code(self, data):
        search = re.search(r'HTTP/1\.. (?P<code>\d*)', data)
        return search.group('code')

    def get_headers(self,data):
        search = re.search(r'(?P<headers>.+?)\r\n\r\n', data, re.DOTALL)
        return search.group('headers')

    def get_body(self, data):
        search = re.search(r'.*?\r\n\r\n(?P<body>.*)', data, re.DOTALL)
        return search.group('body')

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
        host, port, path = self.get_host_port(url)
        #print host, port, path
        self.connect(host, port)
        request = "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path, host)
        self.sock.sendall(request)
        data = self.recvall(self.sock)
        self.sock.close()
        headers = self.get_headers(data)
        code = int(self.get_code(headers))
        body = self.get_body(data)
        #print body
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.get_host_port(url)
        if args!=None:
            post_data = urllib.urlencode(args)
        self.connect(host, port)
        request = "POST %s HTTP/1.1\r\nHost: %s\r\n" % (path, host)
        if args!=None:
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
        if args!=None:
            request += "Content-Length: %d\r\n" % len(post_data)
        request += "Connection: close\r\n\r\n"
        if args!=None:
            request += post_data
        self.sock.sendall(request)
        data = self.recvall(self.sock)
        self.sock.close()
        headers = self.get_headers(data)
        code = int(self.get_code(headers))
        body = self.get_body(data)
        print headers, body
        return HTTPResponse(code, body)

    def command(self, command, url, args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
