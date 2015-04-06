Ansible
=======

Ansible is a communication library for talking to Daemon.

You need to run a socket_bridge:

`
cd socket_bridge
npm install # only need to do this once
npm start
`

and then import the ansible library in your python program:

`
import ansible
ansible.init() # initialize connection
ansible.send('string')
ansible.send({'type': 'dictionary', 'dictionary': {}, 'list': []})
ansible.recv()
`

`ansible.recv()` is non-blocking, and will return `None` if there is no message currently in the mailbox.
