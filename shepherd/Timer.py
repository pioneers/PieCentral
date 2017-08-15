class Timer:
	'''
	This class should spawn another thread that will keep track of a target time
	and compare it to the current system time in order to see how much time is left
	'''
	def __init__(self):

	def startTimer(self, duration):
		'''
		Starts a new timer with the duration which is given in seconds
		'''

	def extendDuration(self, duration):
		'''
		Adds time to the timer based on the duration which is given in seconds
		'''

	def getTimeLeft(self):
		'''
		Returns the amount of time left in seconds
		Returns -1 if the most recent timer has expired/there is no timer being tracked
		'''