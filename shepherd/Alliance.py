class Alliance:
    '''
    This is a wrapper that holds both classes and then holds information relevant to
    and it should also contain information relevant to the alliance such as match score
    '''

    def __init__(self, team1, team2):
        self.team_one = team1
        self.team_two = team2
        self.score = 0
        self.large_penalties = 0
        self.small_penalties = 0
        self.multiplier = 1

    def heartbeat(self):
        '''
        Checks if both teams have a robot connected
        '''
        return self.team_one.heartbeat() and self.team_two.heartbeat()

    def add_large_penalty(self):
        '''
        Adds an additional large penalty to this alliance
        '''
        return

    def add_small_penalty(self):
        '''
        Adds an additional small penalty to this alliance
        '''
        return

    def increase_score(self, amount): # pylint: disable=unused-argument
        '''
        Increases this alliance's score by amount
        '''
        return
