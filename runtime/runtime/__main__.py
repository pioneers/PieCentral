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
@click.option('-c', '--config-path', type=click.Path(dir_okay=False, exists=True),
              default=get_module_path('config/default.yaml'), help='Configuration file path')
@click.option('-d', '--dev-schema-path', type=click.Path(dir_okay=False, exists=True),
              default=get_module_path('config/devices.yaml'), help='Device schema path')
def run(**options):
    """ Execute runtime. """
    asyncio.run(runtime.supervisor.start(**options))


@cli.command()
def version():
    """ Print the PiE Runtime version and exit. """
    print(runtime.get_version())


if __name__ == '__main__':
    cli()
