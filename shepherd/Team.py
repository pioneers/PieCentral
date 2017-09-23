class Team:
    '''
    Establishes connection to the team's driver station, contains information such as their
    team's name and number. This is the bridge between the driver stations and Shepherd
    '''

    def __init__(self, teamName, teamNumber):
        self.name = teamName
        self.number = teamNumber

    def send_to_driver(self, message):
        '''
        Uses LCM communication to send a message from the driver station
        '''

    def receive_from_driver(self, message):
        '''
        Uses LCM communication to receive a message from the driver station
        '''

    def heartbeat(self):
        '''
        Returns a boolean indicating if the robot to the team is connected and alive
        '''
