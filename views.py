from flask import jsonify
from flask import render_template
from flask import request
from flask import Flask
from random import randint
from serial import Serial

app = Flask(__name__)

def read_sensor_data():
	port = "COM3"
	baudrate = 9600
	with Serial(port=port, baudrate=baudrate, timeout=1) as Port:
		Port.flushInput()    
		line = Port.readline().decode().strip()
		while line == "":
			line = Port.readline().decode().strip()
		Port.close()
	return {item.split(':')[0]:item.split(':')[1] for item in line.split()}

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/sensor_data")
def sensor_data():
	sensor_data = read_sensor_data()
	return jsonify(temperature=sensor_data['Temperature'], humidity=sensor_data['Humidity'])
