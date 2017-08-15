class Alliance:
	'''
	This is a wrapper that holds both classes and then holds information relevant to 
	and it should also contain information relevant to the alliance such as match score
	'''

	def __init__(self, team1, team2):
		self.teamOne = team1
		self.teamTwo = team2
		self.score = 0
		self.largePenalties = 0
		self.smallPenalties = 0
		self.multiplier = 1

	def heartbeat(self):
		'''
		Checks if both teams have a robot connected
		'''
		return self.teamOne.heartbeat() and self.teamTwo.heartbeat()

	def addLargePenalty(self):
		'''
		Adds an additional large penalty to this alliance
		'''

	def addSmallPenalty(self):
		'''
		Adds an additional small penalty to this alliance
		'''

	def increaseScore(self, amount):
		'''
		Increases this alliance's score by amount
		'''

