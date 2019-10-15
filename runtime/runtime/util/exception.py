class EmergencyStopException(SystemExit):
    """
    A special exception used to indicate an emergency stop (e-stop).

    The exit code 255 is used to communicate from child processes to the
    supervisor that an e-stop has occurred.
    """

    EXIT_CODE = 0xFF

    def __init__(self):
        super().__init__(self.EXIT_CODE)


class RuntimeBaseException(Exception):
    pass
