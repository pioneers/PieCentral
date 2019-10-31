# Field Control API

`class RuntimeClient(host: str[, cmd_port: int])`

* `set_alliance(alliance: str)`, where `alliance` is `'blue', 'gold', 'none'`
* `set_mode(mode: str)`, where `mode` is `'auto', 'teleop', 'idle', 'estop'` (robot begins executing student code)
* `set_starting_zone(zone: str)`, where `zone` is `'left', 'right', 'none'`
* `run_coding_challenge(seed: int[, timeout: float])` (`timeout` is optional in seconds)
* `list_device_names() -> Mapping[str, str]`: Maps UIDs to names
* `set_device_name(uid: str, name: str)`
* `del_device_name(uid: str)`

[Request message format](https://github.com/msgpack-rpc/msgpack-rpc/blob/master/spec.md#request-message)
