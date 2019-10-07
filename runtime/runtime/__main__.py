import asyncio
import os

import click
import yaml

import runtime
import runtime.server


def get_module_path(filename: str) -> str:
    """ Return a path relative to the module's top-level directory. """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, filename)


@click.group()
def cli(**options):
    pass


@cli.command()
@click.option('-c', '--config',
              type=click.Path(dir_okay=False, exists=True),
              default=get_module_path('config/default.yaml'),
              help='Configuration file')
def server(**options):
    """
    Run the PiE Runtime server.
    """
    runtime.server.bootstrap(**options)


@cli.command()
def client(**options):
    """
    Run the PiE Runtime client.
    """


@cli.command()
def version():
    """ Print the PiE Runtime version and exit. """
    print('.'.join(map(str, runtime.__version__)))


if __name__ == '__main__':
    cli()
