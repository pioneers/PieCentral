import math
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
            num_rats - Integer tracking the number of rats on this side
    """

    def __init__(self, name, team_1_name, team_1_number, team_2_name,
                 team_2_number, num_rats = 3, team_1_custom_ip=None, team_2_custom_ip=None):
        self.name = name
        self.team_1_name = team_1_name
        self.team_2_name = team_2_name
        self.team_1_number = team_1_number
        self.team_2_number = team_2_number
        self.score = 0
        self.team_1_connection = False
        self.team_2_connection = False
        self.team_1_custom_ip = team_1_custom_ip
        self.team_2_custom_ip = team_2_custom_ip
        self.num_rats = rat_number
        self.king_rat = king_rat

    def change_score(self, amount):
        """ changes score of this alliance by Amount,
            Amount can be negative or positive.
        """
        self.score += amount
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
                 {"alliance" : self.name, "score" : math.floor(self.score)})

    def reset(self):
        self.score = 0
        self.team_1_connection = False
        self.team_2_connection = False
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
                 {"alliance" : self.name, "score" : math.floor(self.score)})
        #TODO: Send info to sensors about reset
        #TODO: Send info to UI about reset
        #TODO: Move score sends to shepherd.py

    def __str__(self):
        return ("<alliance: " + self.name + "> <teams: " + self.team_1_name + " " +
                str(self.team_1_number) + ", " + self.team_2_name + " " + str(self.team_2_number) +
                "> <score: " + str(self.score) + ">")
