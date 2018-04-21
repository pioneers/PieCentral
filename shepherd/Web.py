class Web:
    '''
    Handles communication between Shepherd and the match Schedule
    '''
    def __init__(self):
        pass

    def get_teams(self, match_number):
        '''
        Returns a list where the first two elements are Team objects
        which correspond to the blue alliance the the next two elements are
        Team objects corresponding to the gold alliance
        '''

    def record_score(self, match_number, blue_score, gold_score):
        '''
        Records the spreadsheet to reflect the scores of the blue and gold alliance.
        Will be called once at the end of a match
        '''
