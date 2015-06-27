Ansible
=======

Ansible is a communication library for talking to Daemon.

From this directory, run a socket_bridge:

1. `cd socket_bridge`
1. `npm install` (only need to do this once)
1. `npm start`

and then import the ansible library in your python program:

1. `import ansible`
1. `ansible.init() # initialize connection`
1. `ansible.send('string')`
1. `ansible.send({'type': 'dictionary', 'dictionary': {}, 'list': []})`
1. `ansible.recv()`

`ansible.recv()` is non-blocking, and will return `None` if there is no message currently in the mailbox.
