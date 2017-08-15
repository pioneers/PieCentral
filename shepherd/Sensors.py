class Sensors:
	'''
	This class will handle receiving information from sensors using pySerial
	The most important method will be updateSensors() which will return a dictionary
	of each sensor's current state

	This version of Sensors.py is configured for the 2018 game - Solar Scramble
	'''

	def __init__(self):
		self.goalSensors = {}
		self.bidStations = {}
		self.mainControls = {}

	def updateSensors(self):
		'''
		This should return a dictionary that maps a sensor name to its current state
		'''