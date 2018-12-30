from setuptools import setup, Extension
from Cython.Build import cythonize
from runtime import __version__

DESCRIPTION = 'PiE runtime daemon'
try:
    with open('README.md') as readme:
        LONG_DESCRIPTION = readme.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

# Inspired by: `https://github.com/kennethreitz/setup.py/blob/master/setup.py`
setup(
    name='runtime',
    version='.'.join(map(str, __version__)),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='PiE Runtime Team',
    author_email='runtime@pioneers.berkeley.edu',
    python_requires='>=3.7.0',
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
        [
            Extension(
                'runtime.buffer',
                ['runtime/buffer.pyx'],
                extra_compile_args=['-lrt', '-lpthread'],
                extra_link_args=['-lrt', '-lpthread'],
            ),
            'runtime/packet.pyx',
        ],
        language_level=3,
        nthreads=4,
    ),
)
