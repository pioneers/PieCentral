import asyncio
import logging

import structlog
import structlog.processors
import structlog.stdlib

from runtime.messaging.routing import Connection


LEVEL: str = 'INFO'
PRETTY: bool = False


def configure_logging(*extra_processors, level: str = None, pretty: bool = None):
    """
    .. _structlog Configuration
        http://www.structlog.org/en/stable/configuration.html
    """
    logging.basicConfig(format='%(message)s', level=(level or LEVEL))

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    processors.extend(extra_processors)

    if pretty or PRETTY:
        renderer = structlog.dev.ConsoleRenderer(pad_event=40)
    else:
        renderer = structlog.processors.JSONRenderer()
        processors.append(structlog.stdlib.render_to_log_kwargs)
    processors.append(renderer)
    logging.getLogger('asyncio').disabled = True

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def make_publisher(log_conn):
    def publish(logger, method_name, event):
        asyncio.create_task(log_conn.send(event))
        return event
    return publish
