"""
Web server that provides a user-facing webpage and
REST API to interact with Hibike. Useful for testing
smart sensors.
"""

from setuptools import setup

setup(
    name="Sensor Testing Web Application",
    version="0.1",
    long_description=__doc__,
    packages=["sensor_testing"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["Flask"]
)
