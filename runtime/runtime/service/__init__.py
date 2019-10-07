from runtime.service.broker import BrokerService
from runtime.service.control import ControlService
from runtime.service.device import DeviceService
from runtime.service.executor import ExecutorService

SERVICES = {
    'control': ControlService,
    'device': DeviceService,
    'executor': ExecutorService,
    'broker': BrokerService,
}
