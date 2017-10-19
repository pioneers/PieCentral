class Timer:
    """
    This class should spawn another thread that will keep track of a target time
    and compare it to the current system time in order to see how much time is left
    """
    def __init__(self, timer_type, goal_name=None):
        """
        timer_type - a Enum representing the type of timer that this is:
                        TIMER_TYPES.BID - represents a bid timer
                        TIMER_TYPES.MATCH - represents the time of the current
                                            stage in the match
                        TIMER_TYPES.COOLDOWN - represents a cooldown timer for
                                               the cooldown when a powerup
                                               cannot be applied
                        TIMER_TYPES.CODE_COOLDOWN - represents a cooldown timer
                                                    for a code
                        TIMER_TYPES.DURATION - represents a duration timer for
                                               a powerup
        """
        self.active = False
        self.timer_type = timer_type
        self.goal_name = goal_name

    def start_timer(self, duration):
        """Starts a new timer with the duration (seconds) and sets timer to active"""
        pass

    def reset(self):
        """Stops the current timer (if any) and sets timer to inactive"""
        pass

    def is_running(self):
        """Returns true if the timer is currently running"""
        return self.active
