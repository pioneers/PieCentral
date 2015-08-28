from grizzly import *

class Motors:
    # initializes Grizzly motor to use default settings
    def __init__(self, addr)
        self.g = Grizzly(addr)
        self.set_settings_default()        

    # No PID, DriveCoast, motor doesn't run
    def set_settings_default(self):
        self.g.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_COAST)
        self.g.limit_acceleration(142)
        self.g.limit_current(10)
        self.reset_motor()

    def reset_motor(self):
        self.g.set_target(0)
    
    def set_mode_PID(self):
        # TODO: figure out what ControlMode and DriveMode do        

    def set_speed(self, speed):
        if speed > 100 or speed < -100:
            print "Please input a speed within -100 to 100."
        else:
            self.g.set_target(speed)
    
    def set_neg_speed(self, speed):
        self.g.set_speed(-1 * speed)
    
    def set_speed_from_controller(self, speed):
        self.g.set_speed(100.0 * speed)

    def set_neg_speed_from_controller(self, speed):
        self.g.set_speed(-100.0 * speed)
   
    # For debug output
    @property
    def speed(self):
        return self.g.get_target()
    
addrs = Grizzly.get_all_ids()
        
#@property
#def addrs(self):
#    self.addrs = Grizzly.get_all_ids()
#     return self.addrs;
 
  
