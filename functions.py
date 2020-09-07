from gpiozero import LED
from serial import Serial
import serial
import time
import plotly
# import plotly.graph_objs as go
import plotly.graph_objects as go
from twilio.rest import Client
from secrets import *


class pump_control:
    """This class is used to manage the AC/DC relay made by Digital Loggers.
       This class will be used to manage the Pump of a NFT hydroponic system.
       Initializing to the last state is used so that if the RPI reboots for some reason,
       it wil continue to work as it was before the reboot."""

    def __init__(self, pin, start_state=None):
        self.switch = LED(pin)
        if start_state:
            if start_state == 'on':
                self.on()
            else:
                self.off()
        else:
            self.init_state()

    def read_state(self):
        with open('pump_state.txt') as file:
            data = file.read().strip()
        return data

    def write_state(self, state):
        with open('pump_state.txt', 'w+') as file:
            file.write(state)

    def on(self):
        self.switch.on()
        self.pump_state = 'on'
        self.write_state(self.pump_state)


    def off(self):
        self.switch.off()
        self.pump_state = 'off'
        self.write_state(self.pump_state)

    def toggle(self):
        if self.pump_state == 'off':
            self.on()
        else:
            self.off()

    def init_state(self):
        ls = self.read_state()
        if ls == 'on':
            self.on()
            self.pump_state = 'on'
        else:
            self.off()
            self.pump_state = 'off'


def fetch_data(Port, timeout):
    Port.reset_input_buffer()
    start = time.time()
    sensors = ['Pulss', 'eTape', 'Humidity', 'Temperature']
    sensor_dictionary = {expected_sensor : None for expected_sensor in sensors}
    while time.time() - start < timeout:
        try:
            line = Port.readline().decode().strip()
            print('line: ', line)
            if line.count(':') == 4:
                for i, item in enumerate(line.split()):
                    sensor_dictionary[sensors[i]] = item.split(':')[1]
                return sensor_dictionary
        except UnicodeDecodeError:
            continue
    return sensor_dictionary



def create_plot(value, last_value, formatting):
    data = [go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = value,
    mode = "gauge+number+delta",
    title = {'text': '<b>' + formatting['Title'] + '</b>', 'font':{'size':14, 'color':'white', }},
    delta = {'reference': last_value},
    gauge = {'axis': {'range': [formatting['Gauge_Min'], formatting['Gauge_Max']], 
                      'ticksuffix' : formatting['Data_Suffix']},
             'steps' : [{'range': [formatting['Highlight_Lower'], formatting['Highlight_Upper']], 'color': "gray"}],
                        'threshold' : {'line': {'color': "green", 'width': 4}, 
                        'thickness': 0.75, 'value': formatting['Line_Threshold']},
                        'bordercolor':'white'})]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON



def send_message(payload, account_sid, messaging_service_sid, auth_token, number):
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
             body=payload,
             messaging_service_sid=messaging_service_sid,
             to=number)

def manage_flow(flow, session_data):
        if (pump.pump_state.title() == 'On') and (time() = session_data['pump_start'] > 20) and (flow < 50):
            send_message(f'Pump flow is currently {flow}%', account_sid, messaging_service_sid, auth_token, number)
        return    

def log_data(data):
    pass

def monitor_pump():
    pass


# if 'linux' in platform:
#     port = '/dev/ttyACM0'
# else:
#     ##For when I am testing arduino on Windows
#     port = "COM3"
# 
# baudrate = 9600
# 
# with Serial(port=port, baudrate=baudrate, timeout=1) as Port:
#     Port.flushInput()    
#     line = Port.readline().decode().strip()
#     start = time.time()
#     while ":" not in line and time.time() - start < 10:
#         line = Port.readline().decode().strip()
#     Port.close()
#     print(line)
