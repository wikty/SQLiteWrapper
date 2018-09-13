def get_generator_params():
	for i in range(100):
		counter_id = 'counter%d' % i
		d = {}
		d[counter_id] = i
		# the return results must match the sql placeholders number and style
		yield d