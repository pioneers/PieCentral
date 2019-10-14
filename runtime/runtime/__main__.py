"""
The runtime command-line interface.
"""

import asyncio
import os

import click
import yaml

import runtime
import runtime.supervisor


def get_module_path(filename: str) -> str:
    """ Return a path relative to the module's top-level directory. """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, filename)


@click.group()
def cli(**options):
    pass


@cli.command(context_settings={'max_content_width': 800})
@click.option('-l', '--log-level', default='INFO', help='Log level emitted',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']))
@click.option('-p', '--log-pretty', is_flag=True, help='Pretty-print log records')
@click.option('-c', '--config-file',
              type=click.Path(dir_okay=False, exists=True),
              default=get_module_path('config/default.yaml'),
              help='Configuration file')
def run(**options):
    """ Execute runtime. """
    asyncio.run(runtime.supervisor.Runtime(**options).main())


@cli.command()
def version():
    """ Print the PiE Runtime version and exit. """
    print(runtime.get_version())


if __name__ == '__main__':
    cli()
