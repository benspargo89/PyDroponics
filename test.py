import json


calendar = {8: 100, 9: 120, 10:200}
def write_calendar(calendar):
	"""write calendar dictionary to JSON"""
	with open('calendar.json', 'w+') as file:
		file.write(json.dumps(calendar))

def read_calendar():
	"""Read calendar dictionary from JSON"""
	with open('calendar.json') as file:
		calendar = json.loads(file.read())
		return calendar


"""Write default calendar to file"""
write_calendar({i:100 for i in range(7,23)})
