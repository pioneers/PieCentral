class EmergencyStopException(SystemExit):
    EXIT_CODE = 0xFF

    def __init__(self):
        super().__init__(self.EXIT_CODE)
