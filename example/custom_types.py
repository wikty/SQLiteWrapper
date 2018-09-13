def example_adapte(obj):
	'''
	Parameters:
		always accept a object
	
	Return:
		return int, float, str or bytes
	'''
	return str(obj) 

def example_convert(bs):
	'''
	Parameters:
		always accept a bytes

	Return:
		should convert and return bytes as the corresonding object
	'''
	return bs.decode('utf8')