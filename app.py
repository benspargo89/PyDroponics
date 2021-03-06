from flask import jsonify, render_template, Flask, Session, request
from serial import Serial
from functions import *
from secrets import *
from time import sleep, time
from gpiozero import PWMLED
import json
from collections import deque 
##Rember to run sudo pigpiod##
import pigpio


session_data = Session()
session_data['last_temp'] = 0
session_data['last_flow'] = 0
session_data['last_humidity'] = 0
session_data['last_level'] = 0
session_data['chart_layout'] = {'width': 365,'height': 175,'margin': {'l': 10, 'r':10, 't':40, 'b':10, 'pad':10}, 'paper_bgcolor':"rgba(0,0,0,0)"}
session_data['temp_layout'] = {"Title":'Temperature', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":75, "Highlight_Lower":65, "Highlight_Upper":85, "Data_Suffix":'°'}
session_data['flow_layout'] = {"Title":'Pump Flow', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":95, "Highlight_Lower":90, "Highlight_Upper":100, "Data_Suffix":'%'}
session_data['humidity_layout'] = {"Title":'Humidity', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":50, "Highlight_Lower":40, "Highlight_Upper":60, "Data_Suffix":'%'}
session_data['level_layout'] = {"Title":'Tank Level', "Gauge_Min":0, "Gauge_Max":10, "Line_Threshold":6, "Highlight_Lower":5, "Highlight_Upper":7, "Data_Suffix":' In.'}
session_data['Port'] = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
session_data['pump_start'] = time()
session_data['flow_record'] = deque([100 for _ in range(10)])
session_data['Light_Control'] = pigpio.pi()
session_data['Light_Pin'] = 13
session_data['Light_Control'].set_PWM_dutycycle(session_data['Light_Pin'], 200)
session_data['Lighting_Calendar'] = read_calendar()
session_data['Calendar_Enabled'] = True 


pump = pump_control(4)
app = Flask(__name__)   


@app.route("/")
def index():
    sensor_data = fetch_data(session_data['Port'], 10)
    temp = float(sensor_data['Temperature'][:-2])
    humidity = float(sensor_data['Humidity'][:-1])
    flow = float(sensor_data['Pulss']) / 51 * 100
    level = float(sensor_data['eTape']) / 687
    level = 6
    temp_chart = create_plot(temp, temp, session_data['temp_layout'])
    flow_chart = create_plot(flow, flow, session_data['flow_layout'])
    humidity_chart = create_plot(humidity, humidity, session_data['humidity_layout'])
    level_chart = create_plot(level, level,  session_data['level_layout'])
    session_data['last_temp'] = temp
    session_data['last_humidity'] = humidity
    session_data['last_flow'] = flow
    session_data['last_level'] = level
    current_state = pump.pump_state.title()
    return render_template("base.html"
                    , temp_chart=temp_chart
                    , flow_chart=flow_chart
                    , humidity_chart=humidity_chart
                    , level_chart=level_chart
                    , chart_layout=session_data['chart_layout']
                    , pump_state=current_state)
    

@app.route("/sensor_data")
def sensor_data():
    sensor_data = fetch_data(session_data['Port'], 10)
    temp = float(sensor_data['Temperature'][:-2])
    humidity = float(sensor_data['Humidity'][:-1])
    flow = float(sensor_data['Pulss']) / 51 * 100
    manage_flow(flow, session_data, pump)
    level = float(sensor_data['eTape']) / 687
    level = 6
    temp_chart = create_plot(temp, session_data['last_temp'], session_data['temp_layout'])
    flow_chart = create_plot(flow, session_data['last_flow'], session_data['flow_layout'])
    humidity_chart = create_plot(humidity, session_data['last_humidity'], session_data['humidity_layout']) 
    level_chart = create_plot(level, session_data['last_level'], session_data['level_layout'])
    payload = jsonify(temp_chart=temp_chart
                    , flow_chart=flow_chart
                    , humidity_chart=humidity_chart
                    , level_chart=level_chart
                    , chart_layout=session_data['chart_layout'])
    session_data['last_temp'] = temp
    session_data['last_humidity'] = humidity
    session_data['last_flow'] = flow
    session_data['last_level'] = level
    if session_data['Calendar_Enabled']:
        session_data['Light_Control'].set_PWM_dutycycle(session_data['Light_Pin'], calendar_light()) 
    return payload


@app.route("/toggle_pump")
def toggle_pump():
    pump.toggle()
    current_state = pump.pump_state.title()
    if current_state == 'on':
        session_data['pump_start'] = time()
    else:
        session_data['flow_record'] = deque([100 for _ in range(10)])
    return jsonify(pump_state=current_state)


@app.route("/adjust_lights", methods=['POST'])
def adjust_light():
    light_value = int(request.form['Value'])
    if light_value != 240:
        set_level = 240 - light_value
    else:
        set_level = 0
    session_data['Light_Control'].set_PWM_dutycycle(session_data['Light_Pin'], set_level)
    return str(set_level)


@app.route("/toggle_calendar")
def toggle_calendar():
    if session_data['Calendar_Enabled']:
        session_data['Calendar_Enabled'] = False
    else:
        session_data['Calendar_Enabled'] = True

    return jsonify(calendar_state=session_data['Calendar_Enabled'])
    # write_calendar(calendar)
    # session_data['Lighting_Calendar'] = read_calendar()

