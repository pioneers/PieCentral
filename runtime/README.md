# Runtime

Refer to the [documentation](docs).

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
