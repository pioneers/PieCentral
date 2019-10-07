__version__ = (2, 0, 0, 'alpha')


def get_version():
    return '.'.join(map(str, __version__[:3])) + '-' + __version__[3]
