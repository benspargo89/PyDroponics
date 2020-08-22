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