from runtime.service.broker import BrokerService
from runtime.service.device import DeviceService
from runtime.service.executor import ExecutorService

SERVICES = {
    'device': DeviceService,
    'executor': ExecutorService,
    'broker': BrokerService,
}
