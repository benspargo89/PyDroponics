from flask import jsonify, render_template, Flask, Session
from serial import Serial
from functions import *

session_data = Session()
session_data['last_temp'] = 0
session_data['last_flow'] = 0
session_data['last_humidity'] = 0
session_data['last_level'] = 0
session_data['chart_layout'] = {'width': 325,'height': 210,'margin': {'l': 10, 'r':10, 't':40, 'b':10, 'pad':10}, 'paper_bgcolor':"rgba(0,0,0,0)"}
session_data['temp_layout'] = {"Title":'Temperature', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":75, "Highlight_Lower":65, "Highlight_Upper":85, "Data_Suffix":'°'}
session_data['flow_layout'] = {"Title":'Pump Flow', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":95, "Highlight_Lower":90, "Highlight_Upper":100, "Data_Suffix":'%'}
session_data['humidity_layout'] = {"Title":'Humidity', "Gauge_Min":0, "Gauge_Max":100, "Line_Threshold":50, "Highlight_Lower":40, "Highlight_Upper":60, "Data_Suffix":'%'}
session_data['level_layout'] = {"Title":'Tank Level', "Gauge_Min":0, "Gauge_Max":10, "Line_Threshold":6, "Highlight_Lower":5, "Highlight_Upper":7, "Data_Suffix":' In.'}



pump = pump_control(4)
app = Flask(__name__)


@app.route("/")
def index():
    sensor_data = read_sensor_data(['Temperature', 'Humidity', 'Pulss', 'eTape'], 15)
    try:
        temp = float(sensor_data['Temperature'][:-2])
        humidity = float(sensor_data['Humidity'][:-1])
        flow = float(sensor_data['Pulss']) / 51 * 100
        level = float(sensor_data['eTape']) / 687
    except:
        print("FAILED TO RETRIEVE DATA")
        temp=last_temp
        humidity=last_humidity
        flow=last_flow
        level=last_level
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
                    , chart_layout=chart_layout
                    , pump_state=current_state)

    

@app.route("/sensor_data")
def sensor_data():
    sensor_data = read_sensor_data(['Temperature', 'Humidity', 'Pulss', 'eTape'], 15)
    print(sensor_data)
    try:
        temp = float(sensor_data['Temperature'][:-2])
        humidity = float(sensor_data['Humidity'][:-1])
        flow = float(sensor_data['Pulss']) / 51 * 100
        level = float(sensor_data['eTape']) / 687
    except:
        print("FAILED TO GET DATA")
        temp = session_data['last_temp']
        flow = session_data['last_flow']
        humidity = session_data['last_humidity']
        level = session_data['last_level']
    level = 6
    temp_chart = create_plot(temp, last_temp, session_data['temp_layout'])
    flow_chart = create_plot(flow, last_flow, session_data['flow_layout'])
    humidity_chart = create_plot(humidity, last_humidity, session_data['humidity_layout']) 
    level_chart = create_plot(level, last_level, session_data['level_layout'])
    payload = jsonify(temp_chart=temp_chart
                    , flow_chart=flow_chart
                    , humidity_chart=humidity_chart
                    , level_chart=level_chart
                    , chart_layout=chart_layout)
    session_data['last_temp'] = temp
    session_data['last_humidity'] = humidity
    session_data['last_flow'] = flow
    session_data['last_level'] = level
    return payload


@app.route("/toggle_pump")
def toggle_pump():
    pump.toggle()
    current_state = pump.pump_state.title()
    return jsonify(pump_state=current_state)



