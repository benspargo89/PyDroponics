from flask import jsonify, render_template, Flask
# from flask import render_template
# from flask import Flask
from serial import Serial
from functions import *

import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
from random import randint as ri

global last_chart_value
last_chart_value = 0

def create_plot(value, last_value):
    formatting = {"Title":'Temperature'
                , "Gauge_Min":0
                , "Gauge_Max":100
                , "Line_Threshold":90
                , "Highlight_Lower":65
                , "Highlight_Upper":85
                , "Data_Suffix":'°'}
    data = [go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = value,
    mode = "gauge+number+delta",
    title = {'text': formatting['Title'], "font":{'size':6 }}, ##, "font":{'size':6 }
    delta = {'reference': last_value},
    gauge = {'axis': {'range': [formatting['Gauge_Min'], formatting['Gauge_Max']], 
                      'ticksuffix' : formatting['Data_Suffix']},
             'steps' : [{'range': [0, 250], 'color': "lightgray"},
                        {'range': [250, 400], 'color': "gray"}],
                        'threshold' : {'line': {'color': "red", 'width': 4}, 
                        'thickness': 0.75, 'value': formatting['Line_Threshold']},
                        'bordercolor':'white'})]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

app = Flask(__name__)


@app.route("/")
def index():
    bar = create_plot(200,last_chart_value)
    print(bar)
    return render_template("base.html", pump_stat="a", plot=bar, plot2=bar)



@app.route("/sensor_data")
def sensor_data():
    global last_chart_value
    expected_sensors = ['Temperature', 'Humidity', 'Pulss', 'eTape']
    timeout = 10
    sensor_data = read_sensor_data(expected_sensors, timeout)
    print(sensor_data)
    chart_val = ri(1,100)
    temp = float(sensor_data['Temperature'][:-2])
    print(temp)
    payload = jsonify(temperature=sensor_data['Temperature']
		    , humidity=sensor_data['Humidity']
		    , chart=create_plot(temp, last_chart_value)
		    , chart2=create_plot(temp, last_chart_value))
    last_chart_value = chart_val
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

