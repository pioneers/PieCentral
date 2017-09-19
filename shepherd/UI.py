class UI: # pylint: disable=too-few-public-methods
    '''
    Handles the main display and information between Shepherd and the webpage
    '''
    def __init__(self):
        pass

    def push_timers(self, dict_of_timers):
        '''
        Sends a message to the webpage letting it know the most recent status of timers
        '''
