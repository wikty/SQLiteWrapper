from .cl_commander import ClCommander

def display(response):
	if response['header']['status'] == 'error':
		print('[ERROR]', response['body'])
	else:
		print(response['body'])

def run(con=None, args=None, dump=None):
	commander = ClCommander(dump)
	display(commander.open(con, args))
	try:
		while True:
			line = input('# ').strip()
			if not line:
				continue
			response = commander.accept(line)
			if response['header']['type'] == 'termination':
				raise KeyboardInterrupt()
			display(response)
	except KeyboardInterrupt:
		response = commander.close()
		display(response)