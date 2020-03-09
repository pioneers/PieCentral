from setuptools import setup, Extension
from Cython.Build import cythonize
from runtime import get_version

DESCRIPTION = 'PiE runtime daemon'
try:
    with open('README.md') as readme:
        LONG_DESCRIPTION = readme.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

# Inspired by: `https://github.com/kennethreitz/setup.py/blob/master/setup.py`
setup(
    name='runtime',
    version=get_version(),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='PiE Runtime Team',
    author_email='runtime@pioneers.berkeley.edu',
    python_requires='>=3.8.0',
    url='https://github.com/pioneers/PieCentral',
    packages=['runtime'],
    install_requires=[
        'click>=7,<8',
        'pyserial>=3,<4',
        'pyudev<1',
    ],
    # See `https://pypi.org/pypi?%3Aaction=list_classifiers` for full list.
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: AsyncIO',
        'Framework :: Pytest',
        'Framework :: Sphinx',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Cython'
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    ext_modules=cythonize(
        ['runtime/messaging/packet.pyx'],
        language_level=3,
        nthreads=4,
    ),
)
