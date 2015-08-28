import ansible
ansible.init()

while True:
    stuff = ansible.recv()
    if stuff:
        print stuff

