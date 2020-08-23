from flask import jsonify
from flask import render_template
##from flask import request
from flask import Flask
from serial import Serial
from functions import *

app = Flask(__name__)
pump = pump_control(4)

@app.route("/")
def index():
    return render_template("base.html", pump_state=pump.pump_state.title())

@app.route("/sensor_data")
def sensor_data():
    expected_sensors = ['Temperature', 'Humidity']
    timeout = 10
    sensor_data = read_sensor_data(expected_sensors, timeout)
    return jsonify(temperature=sensor_data['Temperature'], humidity=sensor_data['Humidity'])


@app.route("/toggle_pump")
def toggle_pump():
    pump.toggle()
    current_state = pump.pump_state.title()
    return jsonify(pump_state=current_state)