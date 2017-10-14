import Utils.py
class Alliance:
    """This is the Alliance class, which holds the state values used to track
       the scores and states of the alliances
            name - an Enum 'GOLD' or 'BLUE' representing the Alliance
            team_1_name - string representing name of first team
            team_2_name - string representing name of second team
            team_1_number - Integer representing team number of first team
            team_2_number - Integer representing team number of second team
            score - Integer tracking the score of the Alliance
            alliance_multiplier - Integer tracking the value of the alliance's
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
                 team_2_number, score):
        self.name = name
        self.team_1_name = team_1_name
        self.team_2_name = team_2_name
        self.team_1_number = team_1_number
        self.team_2_number = team_2_number
        self.score = score
        self.alliance_multiplier = 1
        self.two_x_cooldown = Timer()
        self.zero_x_cooldown = Timer()
        self.steal_cooldown = Timer()
        self.code_cooldown = Timer()

    def change_score(ammount):
        """ changes score of this alliance by Amount,
            Ammount can be negative or positive.
            make sure you update the scoreboad too after using this function
        """
        self.score += ammount
