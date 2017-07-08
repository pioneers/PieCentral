# Licensed to Pioneers in Engineering under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Pioneers in Engineering licenses
# this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--persistent", help="persistent sending mode",
                    action="store_true")
parser.add_argument("--ip", default='localhost',
                    help="destination ip, default localhost")
parser.add_argument("--port", default='3141',
                    help="connection port, default 3141")
args = parser.parse_args()


HOST = args.ip
PORT = int(args.port)
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        msg = bytes(input('message: '), 'UTF8')
        s.sendall(msg)
    if not args.persistent:
        break

