import io
from runtime.util import RuntimeBaseException


class ReadDisabledError(RuntimeBaseException):
    def __init__(self, sensor_name, param_name):
        super().__init__(f'Cannot read parameter "{param_name}" of sensor "{sensor_name}".')


class WriteDisabledError(RuntimeBaseException):
    def __init__(self, sensor_name, param_name):
        super().__init__(f'Cannot write parameter "{param_name}" of sensor "{sensor_name}".')


class Actions:
    @staticmethod
    async def sleep(seconds: float):
        await asyncio.sleep(seconds)


class Field:
    def __init__(self, client):
        self.client = client

    @property
    def alliance(self):
        pass

    @property
    def starting_zone(self):
        pass


class Gamepad:
    def __init__(self):
        pass

    def get_value(self, name: str):
        pass


class Robot:
    def __init__(self):
        pass

    def get_value(self, dev_id: str, param: str):
        pass

    def set_value(self, dev_id: str, param: str, value):
        pass

    def run(self, async_fn, *args):
        pass

    def is_running(self, async_fn):
        pass

    def emergency_stop(self):
        pass

    def get_timestamp(self):
        pass
