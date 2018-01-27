from flask import Flask
APP = Flask(__name__)

# pylint: disable=wrong-import-position
import sensor_testing.interface
