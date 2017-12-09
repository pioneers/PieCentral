import LCM
import queue
from Utils import *

class Sensors: # pylint: disable=too-few-public-methods
    '''
    This class will handle receiving information from sensors using pySerial
    The most important method will be updateSensors() which will return a dictionary
    of each sensor's current state

    This version of Sensors.py is configured for the 2018 game - Solar Scramble
    '''

    def __init__(self):
        self.goal_sensors = {}
        self.bid_stations = {}
        self.main_controls = {}
        self.event_map = {SENSOR_HEADER.CODE_RESULT: code_result, }
        self.event_queue = queue.Queue()
        LCM.start_read(LCM_TARGETS.LCM_TARGET_SENSORS, self.event_queue)

    def code_result(self, result, team):
    	self.bid_stations[team].write(result)
    	self.prev_powerup = result

    def failed_powerup(self, team):
    	self.bid_stations[team].write(self.prev_powerup)

    def bid_update(self, bids):
    	gold = self.bid_stations[ALLIANCE_COLOR.GOLD]
    	blue = self.bid_stations[ALLIANCE_COLOR.BLUE]

    	for i in range(len(bids)):
    		gold.write(bids[i])
    		blue.write(bids[i])

    def update_sensors(self):
        '''
        This should return a dictionary that maps a sensor name to its current state
        '''

    def main(self):
    	while True:
    		event = self.event_queue.get(True)
    		header = event[0]
    		args = 