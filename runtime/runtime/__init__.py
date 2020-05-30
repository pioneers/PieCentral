import asyncio
import pathlib

import zmq
import zmq.devices

from runtime import log
from runtime.frame import Frame
from runtime.service.storage import Document, DocumentService
from runtime.service.supervisor import SupervisorService


__version__ = (2, 0, 0, 'a0')


async def run(**options):
    config = DocumentService(pathlib.Path(options['config']))
    await config.load()
    names = DocumentService(pathlib.Path(options['names']))
    await names.load()
    await log.start_log_proxy(config)
    await Frame.catalog.load(DocumentService(pathlib.Path(options['catalog'])))
    address = await config.get('supervisor.addresses.rpc')
    supervisor = SupervisorService(names, address, config, debug=options['debug'])
    await supervisor.run()


def get_version() -> str:
    return '.'.join(map(str, __version__[:3])) + str(__version__[3])
