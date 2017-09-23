"""
class Goal:

    def __init__(self):
        self.goal_state = 0 #unowned, blueowned, goldowned, bluebid, goldbid
        self.bid_timer = timer thread(sends to shepherd main)
        self.multiplier_timer
        self.goal_multiplier
        self.price
        self.alliance = alliance_object

class Alliance:

    self.score
    self.score_multiplier
    self.increase_score()

class Timer:
    gameTime(gameState):
        starts with StateChange(Active)
        write to queue current time reamining
        at end, writes statechange(idle)

    sensorCooldown(side):
        write to queue current time remaining
        at end, sets both sensor multipiers to not used




class Utils:
    AutoStateTimePeriod
    TeleopStateTimePeriod
    BiddingMulitplierValue
    BiddingTimeStartVAlue
    BiddingAdditionaTimeValue
    ScoreMultiplierValues
    GoalMultiplierValues
    GoalMulitpliercooldowns

"""
