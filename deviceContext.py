class DeviceContext():
	def __init__(self):
		#contextData = {uid: ({param: (value, timestamp)}, delay, timestamp) }
		self.contextData = dict()

	def getData(self, uid, param):
		if uid in self.contextData:
			if param in self.contextData[uid]:
				return self.contextData[uid][param]
			else:
				return "The parameter {0} does not exist for your specified device.".format(param)
		else:
			return "You have not specified a valid device. Check your UID."


	def getDelay(self, uid):
		if uid in self.contextData:
			return (self.contextData[uid][1], self.contextData[uid][2])
		else:
			return "You have not specified a valid device. Check your UID."


	def subToDevices(self, deviceTupeles):

	def subDevice(self, uid):

	def writeValue(self, uid, param, value):
