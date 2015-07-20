from grizzly import *
import ansible

# Grizzly setup stuff
addrs=Grizzly.get_all_ids()
gs=[]
for addr in addrs:
    g = Grizzly(addr)
    g.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_COAST)
    g.limit_acceleration(142)
    g.limit_current(10)
    gs.append(g)

for g in gs:
    g.set_target(0)

while True:
    command = ansible.recv()
    if command:
        print command
        header = command['header']
        content = command['content']
        if header['msg_type'] == 'gamepad' and content:
            gamepad = content[0]
            gs[0].set_target(100.0*gamepad['axes'][1])
            gs[1].set_target(-100.0*gamepad['axes'][3])
