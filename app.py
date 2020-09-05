from flask import jsonify, render_template, Flask
from serial import Serial
from functions import *

import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go


global last_temp
global last_flow
global last_humidity
global last_level
last_temp = 0
last_flow = 0
last_humidity = 0
last_level = 0

    
def create_plot(value, last_value, formatting):
    data = [go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = value,
    mode = "gauge+number+delta",
    title = {'text': formatting['Title']},
	delta = {'reference': last_value},
    gauge = {'axis': {'range': [formatting['Gauge_Min'], formatting['Gauge_Max']], 
                      'ticksuffix' : formatting['Data_Suffix']},
             'steps' : [{'range': [formatting['Highlight_Lower'], formatting['Highlight_Upper']], 'color': "gray"}],
                        'threshold' : {'line': {'color': "green", 'width': 4}, 
                        'thickness': 0.75, 'value': formatting['Line_Threshold']},
                        'bordercolor':'white'})]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

app = Flask(__name__)


@app.route("/")
def index():
    global last_temp
	global last_flow
	global last_humidity
	global last_level
    sensor_data = read_sensor_data(['Temperature', 'Humidity', 'Pulss', 'eTape'], 15)
    temp = float(sensor_data['Temperature'][:-2])
    humidity = float(sensor_data['Humidity'][:-1])
    flow = float(sensor_data['Pulss']) / 60
    level = float(sensor_data['eTape']) / 687
    temp_chart = create_plot(temp, last_temp, {"Title":'Temperature', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":75, "Highlight_Lower":65, "Highlight_Upper":85, "Data_Suffix":'°'})
    flow_chart = create_plot(flow, last_flow, {"Title":'Pump Flow', "Gauge_Min":0, "Gauge_Max":120, "Line_Threshold":100, "Highlight_Lower":95, "Highlight_Upper":105, "Data_Suffix":'%'})
    humidity_chart = create_plot(humidity, last_humidity, {"Title":'Humidity', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":50, "Highlight_Lower":40, "Highlight_Upper":60, "Data_Suffix":'%'})
    level_chart = create_plot(level, last_level, {"Title":'Tank Level', "Gauge_Min":0, "Gauge_Max":10, "Line_Threshold":6, "Highlight_Lower":5, "Highlight_Upper":7, "Data_Suffix":' In.'})
    last_temp = temp
    last_humidity = humidity
    last_flow = flow
    last_level = level

    return render_template("base.html", temp_chart=create_plot(temp, temp, temp_chart)
					, flow_chart=create_plot(flow, flow, flow_chart)
					, humidity_chart=create_plot(humidity, humidity, humidity_chart)
					, level_chart=create_plot(level, level, level_chart))

    # return render_template("base.html", pump_stat="a", temp_chart=bar, flow_chart=bar, humidity_chart=bar, level_chart=bar)



@app.route("/sensor_data")
def sensor_data():
    global last_temp
	global last_flow
	global last_humidity
	global last_level

    sensor_data = read_sensor_data(['Temperature', 'Humidity', 'Pulss', 'eTape'], 15)
    temp = float(sensor_data['Temperature'][:-2])
    humidity = float(sensor_data['Humidity'][:-1])
    flow = float(sensor_data['Pulss']) / 60
    level = float(sensor_data['eTape']) / 687
    temp_chart = create_plot(temp, last_temp, {"Title":'Temperature', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":75, "Highlight_Lower":65, "Highlight_Upper":85, "Data_Suffix":'°'})
    flow_chart = create_plot(flow, last_flow, {"Title":'Pump Flow', "Gauge_Min":0, "Gauge_Max":120, "Line_Threshold":100, "Highlight_Lower":95, "Highlight_Upper":105, "Data_Suffix":'%'})
    humidity_chart = create_plot(humidity, last_humidity, {"Title":'Humidity', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":50, "Highlight_Lower":40, "Highlight_Upper":60, "Data_Suffix":'%'})
    level_chart = create_plot(level, last_level, {"Title":'Tank Level', "Gauge_Min":0, "Gauge_Max":10, "Line_Threshold":6, "Highlight_Lower":5, "Highlight_Upper":7, "Data_Suffix":' In.'})
    payload = jsonify(temp_chart=create_plot(temp, last_temp, temp_chart)
					, flow_chart=create_plot(flow, last_flow, flow_chart)
					, humidity_chart=create_plot(humidity, last_humidity, humidity_chart)
					, level_chart=create_plot(level, last_level, level_chart))
    last_temp = temp
    last_humidity = humidity
    last_flow = flow
    last_level = level
    return payload


@app.route("/toggle_pump")
def toggle_pump():
    pump.toggle()
    current_state = pump.pump_state.title()
    return jsonify(pump_state=current_state)


# @app.route("/toggle_pump")
# def toggle_pump():
#     return jsonify(pump_state='on')


# app = Flask(__name__)
# pump = pump_control(4)

# @app.route("/")
# def index():
#     return render_template("base.html", pump_state=pump.pump_state.title())

# @app.route("/sensor_data")
# def sensor_data():
#     expected_sensors = ['Temperature', 'Humidity']
#     timeout = 10
#     sensor_data = read_sensor_data(expected_sensors, timeout)
#     return jsonify(temperature=sensor_data['Temperature'], humidity=sensor_data['Humidity'])

