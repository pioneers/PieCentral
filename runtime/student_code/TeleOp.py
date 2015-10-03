# -------
# TeleOp.py class. Runs the robot.
# Student run this class. 
# -------

    
    # Use this method to write any setup items that
    # need to occur before you run teleop 
    def __init__(self):
        self.robot = Robot()
        self.gamepads = Gamepads.get_gamepads()
        self.sensors = Sensors()       

        # Example
        motor0 = robot.motors[0]
        motor1 = robot.motors[1]
        motor2 = robot.motors[2]
        motor3 = robot.motors[3]
        while True:
            
            left_motor = gamepad.axes(0)[1]
            right_motor = gamepad.axes(0)[3]
            set_motor('motor1', left_motor * 100);
            set_motor('motor3', right_motor * 100);
            # motor2.set_speed(75)
            # motor3.set_speed(10)
     
