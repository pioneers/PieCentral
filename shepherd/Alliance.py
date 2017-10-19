from Utils import *
from Timer import *


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
            two_x_cooldown - Timer representing the time untill the alliance
                             can use another 2x powerup
            zero_x_cooldown - Timer representing the time untill the alliance
                              can use another 0x powerup
            steal_cooldown - Timer representing the time untill the alliance
                             can use another steal powerup
            code_cooldown - Timer representing the time untill the alliance can
                            submit another code
    """

    def __init__(self, name, team_1_name, team_2_name, team_1_number,
                 team_2_number):

        self.name = name
        self.team_1_name = team_1_name
        self.team_2_name = team_2_name
        self.team_1_number = team_1_number
        self.team_2_number = team_2_number
        self.score = 0
        self.alliance_multiplier = 1
        self.two_x_cooldown = Timer(TIMER_TYPES.COOLDOWN)
        self.zero_x_cooldown = Timer(TIMER_TYPES.COOLDOWN)
        self.steal_cooldown = Timer(TIMER_TYPES.COOLDOWN)
        self.code_cooldown = Timer(TIMER_TYPES.CODE_COOLDOWN)

    def change_score(self, amount):
        """ changes score of this alliance by Amount,
            Amount can be negative or positive.
            make sure you update the scoreboad too after using this function
        """
        self.score += amount
