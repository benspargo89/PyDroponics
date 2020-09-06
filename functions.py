from gpiozero import LED
from serial import Serial
import time
from sys import platform
import plotly
import plotly.graph_objs as go
import json
import plotly.graph_objects as go

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

def read_sensor_data(expected_sensors, timeout):
    """This function reads serial data from an Arduino Uno.
       The Arduino receives data from a number of sensors, including
       temerature, humidity, water level, and water flow rate.
       Future additions will likely include PH and EC"""

    """To find port
        1. Before plugging in Arduino, run command: sudo ls /dev/tty*
        2. Plugin Arduino and run command above.
        3. Identify which tty was added, write that one as the port below"""

    if 'linux' in platform:
        port = '/dev/ttyACM0'
    else:
        ##For when I am testing arduino on Windows
        port = "COM3"

    baudrate = 9600
    # try:
    with Serial(port=port, baudrate=baudrate, timeout=20) as Port:
        Port.reset_input_buffer()
        line = Port.readline().decode().strip('\n')
        print('First Read', line)
        start = time.time()
        while "Temperature" not in line and time.time() - start < timeout:
            line = Port.readline().decode().strip('\n')
            print(line)
        Port.close()

    sensor_dictionary = {expected_sensor : None for expected_sensor in expected_sensors}

    """Write sensor values to sensor dictionary.
    This method and a timeout is used so that we see blank values if sensor fails to
    return data in specified timeout"""
    for item in line.split():
        sensor  = item.split(':')[0]
        reading = item.split(':')[1]
        if sensor in expected_sensors:
            sensor_dictionary[sensor] = reading
    # except:
    #     sensor_dictionary = {expected_sensor : None for expected_sensor in expected_sensors}        

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






##to do

def send_text(message):
    pass

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
