"""
The runtime command-line interface.
"""

import asyncio

import click
import yaml

import runtime
import runtime.supervisor
from runtime.util import get_module_path


@click.group()
def cli(**options):
    pass


@cli.command(context_settings={'max_content_width': 800})
@click.option('-l', '--log-level', default='INFO', help='Log level emitted',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']))
@click.option('-p', '--log-pretty', is_flag=True, help='Pretty-print log records')
@click.option('--log-frontend', default='ipc:///tmp/log.sock')
@click.option('--log-backend', default='tcp://*:6003')
@click.option('-c', '--srv-config-path', type=click.Path(dir_okay=False, exists=True),
              default=get_module_path('config/srv-default.yaml'),
              help='Service configuration file path')
@click.option('-d', '--dev-schema-path', type=click.Path(dir_okay=False, exists=True),
              default=get_module_path('config/devices.yaml'), help='Device schema path')
@click.option('-m', '--max-retries', default=8, help='Maximum number of retries')
@click.option('-r', '--retry-interval', default=4, help='Duration between retries')
def run(**options):
    """ Execute runtime. """
    asyncio.run(runtime.supervisor.start(**options))


@cli.command()
def version():
    """ Print the PiE Runtime version and exit. """
    print(runtime.get_version())


if __name__ == '__main__':
    cli()
