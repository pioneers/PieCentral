"""
The runtime command-line interface.
"""

import os
import platform
import click
from runtime import __version__
import runtime.journal
import runtime.monitoring
from runtime.util import read_conf_file, RuntimeBaseException


def get_module_path(filename: str) -> str:
    """ Return a path relative to the module's top-level directory. """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, filename)


def override_options(options: dict):
    """ Override options with mandatory defaults. """
    if 'linux' not in platform.system().casefold():
        options['poll'] = True


@click.command()
@click.option('-r', '--max-respawns', default=3,
              help='Number of times to attempt to respawn a failing subprocess.')
@click.option('--fail-reset', default=120,
              help='Seconds before the subprocess failure counter is reset.')
@click.option('--terminate-timeout', default=5,
              help='Timeout in seconds for subprocesses to terminate.')
@click.option('--student-freq', default=20, help='Student code execution frequency in Hertz.')
@click.option('--stream-freq', default=40, help='Streaming server frequency in Hertz.')
@click.option('--host', default='127.0.0.1', help='Hostname to bind servers to.')
@click.option('--tcp', default=6020, help='TCP port.')
@click.option('--udp-send', default=6021, help='UDP send port.')
@click.option('--udp-recv', default=6022, help='UDP receive port.')
@click.option('-p', '--poll', is_flag=True, help='Poll for hotplugged sensors. '
              'By default, sensors are detected asynchronously with udev. '
              'For non-Linux platforms without udev, this flag is always set.')
@click.option('--poll-period', default=0.04, help='Hotplug polling period.')
@click.option('--monitor-period', default=60, help='Monitor logging period.')
@click.option('-l', '--log-level', default='INFO', help='Lowest visible log level.',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']))
@click.option('--dev-schema', default=get_module_path('conf/device-schema.yaml'),
              help='Path to device schema.', type=click.Path(exists=True, dir_okay=False))
@click.option('--dev-names', default=get_module_path('conf/device-names.yaml'),
              help='Path to device names map.', type=click.Path(dir_okay=False))
@click.option('-s', '--student-code', default=get_module_path('studentcode.py'),
              type=click.Path(exists=True, dir_okay=False),
              help='Path to student code module.')
@click.option('--baud-rate', default=115200, help='Smart sensor baud rate.')
@click.option('--exec-srv', default='/tmp/executor-srv.sock',
              help='Path to the internal executor server.')
@click.option('--net-srv', default='/tmp/networking-srv.sock',
              help='Path to the internal networking server.')
@click.option('--ipc-timeout', default=5, help='Timeout for IPC.')
@click.option('--stat-period', default=60, help='Period for logging statistics.')
@click.option('-c', '--config', default=get_module_path('conf/config.yaml'),
              type=click.Path(dir_okay=False),
              help='Path to configuration file. Overrides any command line options.')
@click.option('-v', '--version', is_flag=True, help='Show the runtime version and exit.')
def cli(version, **options):
    """
    The PiE runtime daemon manages the state of a robot, controls student code
    execution, and communicates with Dawn and Shepherd.
    """
    if version:
        print('.'.join(map(str, __version__)))
    else:
        try:
            options.update(read_conf_file(options['config']))
        except (FileNotFoundError, RuntimeBaseException):
            pass
        override_options(options)
        runtime.journal.initialize(options['log_level'])
        runtime.monitoring.bootstrap(options)


if __name__ == '__main__':
    cli()
