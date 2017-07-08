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

import sys

from runtimeUtil import *


class HibikeSimulator:
    def __init__(self, badThingsQueue, toManager, fromManager):
        self.badThingsQueue = badThingsQueue
        self.fromManager = fromManager
        self.toManager = toManager
        self.commandMapping = self.makeCommandMap()  # dict with command names

    def makeCommandMap(self):
        commandMapping = {
            HIBIKE_COMMANDS.SUBSCRIBE: self.subscribe_device,
        }
        return commandMapping

    def subscribe_device(self, uid, delay, params):
        self._device_subscribed()

    def _device_subscribed(self, uid=123, delay=321, param1="param1", param2="param2"):
        self.toManager.put([HIBIKE_RESPONSE.DEVICE_SUBBED,
                            [uid, delay, [param1, param2]]])

    def emergency_stop(self):
        # should write 0 to all motors and set stopped boolean to true
        print("EMERGENCY STOPPED COMMAND")

    def start(self):
        # TODO: Make sure request is a list/tuple before attempting to access
        # And that there are the correct number of elements
        while True:
            request = self.fromManager.recv()
            cmdType = request[0]
            args = request[1]
            if(len(request) != 2):
                self.badThingsQueue.put(BadThing(sys.exc_info(
                ), "Wrong input size, need list of size 2", event=BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace=False))
            elif(cmdType not in self.commandMapping):
                self.badThingsQueue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (
                    request,), event=BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace=False))
            else:
                command = self.commandMapping[cmdType]
                command(*args)
