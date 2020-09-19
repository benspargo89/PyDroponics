from gpiozero import LED
from serial import Serial
import serial
from time import time, sleep
import plotly
# import plotly.graph_objs as go
import plotly.graph_objects as go
from twilio.rest import Client
from secrets import *
import json


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
    """Gread data from serial port"""
    Port.reset_input_buffer()
    start = time()
    sensors = ['Pulss', 'eTape', 'Humidity', 'Temperature']
    sensor_dictionary = {expected_sensor : None for expected_sensor in sensors}
    while time() - start < timeout:
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
    """Function to render gauges on main page"""
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
    """Use Twilio API to send text message. SIDs, token, are stored in secrets.py file"""
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
             body=payload,
             messaging_service_sid=messaging_service_sid,
             to=number)


def manage_flow(flow, session_data, pump):
    """Manage the flow of the pump given the current flow"""
    if (time() - session_data['pump_start'] > 75) and (pump.pump_state.title() == 'On'):     
        session_data['flow_record'].popleft()
        session_data['flow_record'].append(flow)
        average_flow = round(sum(session_data ['flow_record']) / len(session_data ['flow_record']), 2)
    else:
        average_flow = 100
    if (pump.pump_state.title() == 'On') and (time() - session_data['pump_start'] > 75) and (flow < 25):
        send_message(f'Current Flow - Pump flow is currently running at {round(flow,2)}%. Average rate is {average_flow}', account_sid, messaging_service_sid, auth_token, number)
        print('\n*****SENDING MESSAGE*****\n')
    elif (pump.pump_state.title() == 'On') and (time() - session_data['pump_start'] > 75) and (average_flow < 60):
        send_message(f'Average Flow - Pump flow is currently running at {round(flow,2)}%. Average rate is {average_flow}', account_sid, messaging_service_sid, auth_token, number)
        print('\n*****SENDING MESSAGE*****\n')
 
    else:
        print(f'PUMP IS RUNNING CORRECTLY. Flow: {flow}. Average Flow: {average_flow}')    
    return  


def write_calendar(calendar):
    """write calendar dictionary to JSON"""
    with open('calendar.json', 'w+') as file:
        file.write(json.dumps(calendar))

def read_calendar():
    """Read calendar dictionary from JSON"""
    with open('calendar.json') as file:
        calendar = json.loads(file.read())
        return calendar

def hour():
    return int(time.strftime('%H'))

def calendar_light():
    return read_calendar()[hour()]


##ToDo
def log_data(data):
    pass



