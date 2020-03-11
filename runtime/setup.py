import setuptools

setuptools.setup(
    name='runtime',
    version='1.5.0',
    author='Pioneers in Engineering',
    author_email='runtime@pioneers.berkeley.edu',
    description='Runtime Daemon',
    url='https://github.com/pioneers/PieCentral',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    package_data={'runtime': ['runtime/hibikeDevices.json', 'namedPeripherals.csv']},
    include_package_data=True,
)
