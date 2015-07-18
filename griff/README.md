Ansible
=======

Ansible is a communication library for talking to Dawn.

To import the ansible library in your python program:

1. `import ansible`
1. `ansible.init() # initialize connection`
1. `ansible.send('string')`
1. `ansible.send({'type': 'dictionary', 'dictionary': {}, 'list': []})`
1. `ansible.recv()`

`ansible.recv()` is non-blocking, and will return `None` if there is no message currently in the mailbox.


`test.py` is provided as a way to test communication with Dawn, it simply prints out any data it receives. Run it with `python test.py`.
