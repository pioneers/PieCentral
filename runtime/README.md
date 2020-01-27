# Runtime

## Getting Started

```
$ pip install -v --pre pyzmq \
  --install-option=--enable-drafts \
  --install-option=--zmq=4.3.2
```

## TODO

- [ ] Try to write zeros to all devices on e-stop
- [ ] Clean up exit handling (persist aliases, close all shared memory and connections, etc)
- [ ] Ensure all data structures are synchronized
- [ ] Unlink Gamepad when done
- [x] Create separate SensorStructure type
