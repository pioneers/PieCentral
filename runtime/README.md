# Runtime

## Getting Started

```sh
$ pip install -v --pre pyzmq \
  --install-option=--enable-drafts \
  --install-option=--zmq=4.3.2
$ pipenv install --dev
$ pipenv run dev
```

## TODO

- [ ] Try to write zeros to all devices on e-stop
- [ ] Clean up exit handling (persist aliases, close all shared memory and connections, etc)
- [ ] Ensure all data structures are synchronized
- [x] Unlink Gamepad when done
- [x] Create separate SensorStructure type
- [ ] Use multiple write packets for too many parameter updates
- [x] Finish Runtime Python client
- [ ] Finish Runtime Node client
- [ ] Integrate Dawn with Runtime
- [ ] Add backpressure
- [ ] Clear out old duty_cycle, other writeable parameters
- [ ] Finish Runtime fctool
- [x] Log to the outside world
- [ ] Keep log open until the very end
- [ ] Motor check
- [ ] Use frozen=True to make immutable dataclasses
- [ ] Use exc_info=exc
- [ ] Use black for code autoformatting
