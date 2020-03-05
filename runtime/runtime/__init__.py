__version__ = (2, 0, 0, 'a0')


def get_version():
    return '.'.join(map(str, __version__[:3])) + str(__version__[3])
