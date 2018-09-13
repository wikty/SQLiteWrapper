class JoinAggregate(object):
	def __init__(self):
		self.sep = ', '
		self.items = []

	# must declare step() method
	def step(self, value, sep=''):
		if sep:
			self.sep = str(sep)
		self.items.append(str(value))

	# must declare finalize() method
	def finalize(self):
		return self.sep.join(self.items)