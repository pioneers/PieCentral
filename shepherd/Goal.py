import Utils.py
class Goal:
    """This class holds the state values for the goal.
            value - An integer representing the point value of the Goal
            owner - An Alliance object representing the current owner of the goal
            current_bid - An integer representing the value of the current bid on this goal
            current_bid_team - An Alliance object representing the team that has submited the most recent bid
            previous_bid - An integer representing the value of the previous bid
            previous_bid_team - An alliance object representing the team that made the previous bid
            bid_timer - A timer tracking the time left to bid
            gold_two_x_timer - A timer tracking how long the 2x powerup applied by the gold team will last
            gold_zero_x_timer - A timer tracking how long the 0x powerup applied by the gold team will last
            blue_two_x_timer - A timer tracking how long the 2x powerup applied by the blue team will last
            blue_zero_x_timer - A timer tracking how long the 0x powerup applied by the blue team will last
    """
    bid_increase_constant = Utils.BID_INCREASE_CONSTANT
    def __init__(self, value):
        self.value = value
        self.owner = None
        self.current_bid = 0
        self.current_bid_team = None
        self.previous_bid = 0
        self.previous_bid_team = None
        self.bid_timer = Timer()
        self.gold_two_x_timer = Timer()
        self.gold_zero_x_timer = Timer()
        self.blue_two_x_timer = Timer()
        self.blue_zero_x_timer = Timer()

    def score(alliance):
        """ modifies the owner alliance's score based on the value of the goal, the current multipliers,
            and the alliances multiplier, if the scorring Alliance is the owning alliance."""

    def calc_multiplier():
        """
