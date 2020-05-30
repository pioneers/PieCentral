"""
The runtime command-line interface.
"""

import asyncio

import click

import runtime
from runtime.util import get_module_path


@click.group()
def cli(**options):
    pass


@cli.command(context_settings={'max_content_width': 800})
@click.option('-c', '--config', type=click.Path(dir_okay=False, exists=True),
              default=get_module_path('config/default.yaml'),
              help='Configuration file path')
@click.option('-k', '--catalog', type=click.Path(dir_okay=False, exists=True),
              default=get_module_path('config/device-catalog.yaml'),
              help='Device catalog path')
@click.option('-n', '--names', type=click.Path(),
              default=get_module_path('config/device-names.yaml'),
              help='Device names path')
@click.option('-d', '--debug', is_flag=True, help='Debug flag')
def run(**options):
    """
    Execute runtime.
    """
    asyncio.run(runtime.run(**options), debug=options['debug'])


@cli.command()
def validate():
    """ Validates a configuration file. """
    pass  # TODO


@cli.command()
def version():
    """ Print the PiE Runtime version and exit. """
    print(runtime.get_version())


if __name__ == '__main__':
    cli()
