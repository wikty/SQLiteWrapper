class IteratorParams(object):
	def __init__(self):
		self.count = 0
		self.max = 10

	def __iter__(self):
		return self

	def __next__(self):
		if self.count > self.max:
			raise StopIteration()
		self.count += 1
		# the return results must match the sql placeholders number and style
		return (self.count,)