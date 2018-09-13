import sqlite3

class AutoAdapteObject(object):

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def self_to_avaiable_sqlite3_data_type(self):
		return "{}, {}".format(self.x, self.y) # int, float, bytes, str

	def __conform__(self, protocol):
		if protocol is sqlite3.PrepareProtocol:
			return self.self_to_avaiable_sqlite3_data_type()