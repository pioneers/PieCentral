# [LCM](https://lcm-proj.github.io/)

[LCM Build Instructions](https://lcm-proj.github.io/build_instructions.html) (Linux or Mac OS strongly recommended)

Make sure to run setup.py (or the setup script for the language you are using).

LCM uses UDP multicast to exchange messages, and can be used for to send byte representations of objects (in Python, using `.encode()`) and user-defined data types. There are [tutorials](https://lcm-proj.github.io/tutorial_general.html) for defining these data types in various languages, using `lcm-gen` to generate language-specific bindings, and using `lcm.publish()` and `lcm.subscribe()` to send and receive messages.

## Using LCM in Shepherd

[LCM Python API](https://lcm-proj.github.io/python/lcm.LCM-class.html#publish)

Read [here](https://lcm-proj.github.io/multicast_setup.html) about initializing an LCM object and what address and TTL to choose.

To communicate over a network, Shepherd uses LCM to send messages to a server, which relays those messages through a websocket.

## Methods
`LCM.py` is a library of two methods for sending and receiving messages using the LCM communications protocol. 

+ ```lcm_start_read(receive_channel, queue, put_json=False):```

Takes in receiving channel name (string), queue (Python queue object) and whether to add received items to queue as JSON or Python dict. Creates thread that receives any message to receiving channel and adds it to queue as tuple (header, dict).
header: string
dict: Python dictionary

+ ```lcm_send(target_channel, header, dic={}):```

Send header (any type) and dic (Python dictionary) to target channel (string).
