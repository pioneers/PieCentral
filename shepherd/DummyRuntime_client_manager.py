from Code import *
def connect_to_robots(team1, team2, team3, team4):
    return Runtime_client_manager(team1, team2, team3, team4)

class Runtime_client_manager:

    class connection:
        def __init__(self, num):
            self.num = num

        def set_mode(self, mode):
            pass

    def __init__(self, team_1, team_2, team_3, team_4):
        self.team_1 = team_1
        self.team_2 = team_2
        self.team_3 = team_3
        self.team_4 = team_4
        self.clients = {team_1: self.connection(1111), team_2: self.connection(2222),
                        team_3: self.connection(3333), team_4: self.connection(4444)}
        self.team_1_code = None
        self.team_2_code = None
        self.team_3_code = None
        self.team_4_code = None

    def set_mode(self, mode):
        pass

    def get_student_solutions(self):
        thingy = {self.team_1: self.team_1_code, self.team_2: self.team_2_code,
                  self.team_3: self.team_3_code, self.team_4: self.team_4_code}
        self.team_1_code = None
        self.team_2_code = None
        self.team_3_code = None
        self.team_4_code = None
        return thingy

    def run_coding_challenge(self, team, code):
        if team == self.team_1:
            self.team_1_code = decode(code)
        if team == self.team_2:
            self.team_2_code = decode(code)
        if team == self.team_3:
            self.team_3_code = decode(code)
        if team == self.team_4:
            self.team_4_code = decode(code)
