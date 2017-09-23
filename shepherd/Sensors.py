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

    def update_sensors(self):
        '''
        This should return a dictionary that maps a sensor name to its current state
        '''
