from Utils import *
from Timer import *
from LCM import *

class Alliance:
    """This is the Alliance class, which holds the state values used to track
       the scores and states of the alliances
            name - an Enum 'GOLD' or 'BLUE' representing the Alliance
            team_1_name - String representing name of first team
            team_2_name - String representing name of second team
            team_1_number - Integer representing team number of first team
            team_2_number - Integer representing team number of second team
            score - Integer tracking the score of the Alliance
            alliance_multiplier - Float tracking the value of the alliance's
                                  multiplier
            two_x_cooldown - Timer representing the time until the alliance
                             can use another 2x powerup
            zero_x_cooldown - Timer representing the time until the alliance
                              can use another 0x powerup
            steal_cooldown - Timer representing the time until the alliance
                             can use another steal powerup
    """

    def __init__(self, name, team_1_name, team_1_number, team_2_name,
                 team_2_number):

        self.name = name
        self.team_1_name = team_1_name
        self.team_2_name = team_2_name
        self.team_1_number = team_1_number
        self.team_2_number = team_2_number
        self.score = 0
        self.alliance_multiplier = 1
        self.two_x_cooldown = Timer(TIMER_TYPES.CODE_COOLDOWN)
        self.zero_x_cooldown = Timer(TIMER_TYPES.CODE_COOLDOWN)
        self.steal_cooldown = Timer(TIMER_TYPES.CODE_COOLDOWN)

    def change_score(self, amount):
        """ changes score of this alliance by Amount,
            Amount can be negative or positive.
        """
        self.score += amount
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
                 {"alliance" : self.name, "score" : self.score})

    def increment_multiplier(self):
        if self.alliance_multiplier == 1:
            self.alliance_multiplier = CONSTANTS.MULTIPLIER_INCREASES[0]
        elif self.alliance_multiplier == CONSTANTS.MULTIPLIER_INCREASES[0]:
            self.alliance_multiplier = CONSTANTS.MULTIPLIER_INCREASES[1]
        elif self.alliance_multiplier == CONSTANTS.MULTIPLIER_INCREASES[1]:
            self.alliance_multiplier = CONSTANTS.MULTIPLIER_INCREASES[2]

    def reset(self):
        self.score = 0
        self.alliance_multiplier = 1
        self.two_x_cooldown.reset()
        self.zero_x_cooldown.reset()
        self.steal_cooldown.reset()
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
                 {"alliance" : self.name, "score" : self.score})
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.ALLIANCE_MULTIPLIER,
                 {"alliance" : self.name, "multiplier" : self.alliance_multiplier})
        #TODO: Send info to sensors about reset
        #TODO: Send info to UI about reset
