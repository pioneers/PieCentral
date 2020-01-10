import logging

import structlog
import structlog.processors
import structlog.stdlib


def configure_logging(level: str = 'INFO', pretty: bool = False):
    logging.basicConfig(format='%(message)s', level=level)

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

    if pretty:
        renderer = structlog.dev.ConsoleRenderer(pad_event=50)
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
