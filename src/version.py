VERSION = (1, 0, 0)


def get_version():
    version = '.'.join(map(str, VERSION))
    return version


__version__ = get_version()