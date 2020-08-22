from gpiozero import LED
import time
        
class pump_control:
    """This class is used to manage the AC/DC relay made by Digital Loggers.
       This class will be used to manage the Pump of a NFT hydroponic system.
       Initializing to the last state is used so that if the RPI reboots for some reason,
       it wil continue to work as it was before the reboot."""
    
    def __init__(self, pin, start_state_on=None):
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
            self.pump_on()
            self.pump_state = 'on'
        else:
            self.switch.off()
            self.pump_state = 'off'
            
 
 
  
def read_sensor_data(expected_sensors, timeout):
    """This function reads serial data from an Arduino Uno.
       The Arduino receives data from a number of sensors, including
       temerature, humidity, water level, and water flow rate.
       Future additions will likely include PH and EC"""
    ##Setup serial
    port = "COM3"
    baudrate = 9600
    
    ##Read serial
    
    with Serial(port=port, baudrate=baudrate, timeout=1) as Port:
        Port.flushInput()    
        line = Port.readline().decode().strip()
        start = time.time()
        while line == "" and time.time() - start < timeout:
            line = Port.readline().decode().strip()
        Port.close()
        
    ##Create dictioary of expected sensors
    sensor_dictionary = {expected_sensor : None for expected_sensor in expected_sensors}
    
    """Write sensor values to sensor dictionary.
    This method and a timeout is used so that we see blank values if sensor fails to
    return data in specified timeout"""
    for item in line.split():
        sensor  = item.split(':')[0]
        reading = item.split(':')[1]
        if sensor in expected_sensors:
            sensor_dictionary[sensor] = reading
        
    return sensor_dictionary
 
 



# def read_sensor_data():
#     """This function reads serial data from an Arduino Uno.
#        The Arduino receives data from a number of sensors, including
#        temerature, humidity, water level, and water flow rate.
#        Future additions will likely include PH and EC"""
# 
#     port = "COM3"
#     baudrate = 9600
#     with Serial(port=port, baudrate=baudrate, timeout=1) as Port:
#         Port.flushInput()    
#         line = Port.readline().decode().strip()
#         while line == "":
#             line = Port.readline().decode().strip()
#         Port.close()
#     return {item.split(':')[0]:item.split(':')[1] for item in line.split()}