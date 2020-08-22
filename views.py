from flask import jsonify
from flask import render_template
from flask import request
from flask import Flask
from random import randint
from serial import Serial
from functions import *

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("base.html")

@app.route("/sensor_data")
def sensor_data():
    expected_sensors = ['Temperature', 'Humidity']
    timeout = 10
    sensor_data = read_sensor_data(expected_sensors, timeout)
    return jsonify(temperature=sensor_data['Temperature'], humidity=sensor_data['Humidity'])
