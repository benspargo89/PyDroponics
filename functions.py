from gpiozero import LED


        
class pump_control:
    def __init__(self, pin, start_state=None):
        self.switch = LED(pin)
        if start_state:
            if start_state == 'on':
                self.pump_on()
            else:
                self.pump_off()
        else:
            self.init_state()
        
    def read_state(self):
        with open('pump_state.txt') as file:
            data = file.read().strip()
        return data
    
    def write_state(self, state):
        with open('pump_state.txt', 'w+') as file:
            file.write(state)
    
    def pump_on(self):
        self.switch.on()
        self.write_state('on')
    
    def pump_off(self):
        self.switch.off()
        self.write_state('off')

    
    def init_state(self):
        ls = self.read_state()
        if ls == 'on':
            self.pump_on()
        else:
            self.switch.off()
            
 
pump = pump_control(4)


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