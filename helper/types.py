import datetime

def datetime_py2sqlite(dt):
	'''
	Parameters:
		accept a datetime.datetime object

	Return:
		convert datetime object to timestamp and will be stored into database
	'''
	return int(datetime.datetime.timestamp(dt))

def datetime_sqlite2py(bs):
	'''
	Parameters:
		always accept a bytes

	Return:
		convert the bytes parameter into datetime object and then return it
	'''
	timestamp = int(bs.decode('utf8'))
	return datetime.datetime.fromtimestamp(timestamp)