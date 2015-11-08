class DeviceContext():
	def __init__(self, deviceParams):
		#contextData = {uid: {field: (value, timestamp)}, delay, timestamp) } 
		self.contextData = dict()
		self.deviceParams = deviceParams
		self.hibike = None

	def getData(uid, field):

	def getDelay(uid):

	def subToDevices(self, deviceTuples):
		for devTup in deviceTuples:
			self.subDevice(uid, delay)

	def subDevice(self, uid, delay):
		assert self.hibike is not None, "DeviceContext needs a pointer to Hibike!"
		self.hibike.sendSubRequest(uid, delay)

	def writeValue(self, uid, param, value):
		assert self.hibike is not None, "DeviceContext needs a pointer to Hibike!"
		assert param in self.deviceParams[getDevice(uid)], "Invalid param for {}".format(getDevice(uid))
		
		self.hibike.sendDeviceUpdate(uid, field, value)