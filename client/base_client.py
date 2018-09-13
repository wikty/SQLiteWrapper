import sqlite3, datetime, sys, re, copy

from ..config import readonly_config, writable_config
from ..commander import SimpleCl
from ..commander import run_cl_client

class BaseClient(object):

	debug_prefix = 'SQLite3'

	def __init__(self, **kwargs):
		config = copy.deepcopy(writable_config)
		config.update(kwargs)
		config.update(readonly_config)
		self.database = config['database']
		self.dump = config['dump']
		self.text_factory = config['text_factory']
		self.waiting_unlock_timeout = config['waiting_unlock_timeout']
		self.enable_row_factory = config['enable_row_factory']
		self.enable_debug = config['enable_debug']
		self.enable_autocommit = config['enable_autocommit']
		self.basic_types = config['basic_types']
		self.detect_types = config['detect_types']
		self.position_parameter_placeholder = config['position_parameter_placeholder']
		self.keyword_parameter_placeholder = config['keyword_parameter_placeholder']
		self.custom_types = {}

		self.connection_args = {
			'database': self.database,
			'timeout': self.waiting_unlock_timeout,
			'detect_types': self.detect_types,
		}
		self.client = sqlite3.connect(**self.connection_args)

		# The progress hander is invoked for every n instructions
		# of the SQLite virtual machine
		self.client.set_progress_handler(None, 0)
		
		# The trace callback to be called for each SQL statement that is actually
		# executed by the SQLite backend.
		self.client.set_trace_callback(config.get('trace_callback', None))

		# Enable traceback in user-defined functions, aggregates, 
		# converters, authorizer callbacks etc.
		if self.enable_debug:
			sqlite3.enable_callback_tracebacks(True)
		else:
			sqlite3.enable_callback_tracebacks(False) # sqlite3 default

		# Support access by column name and index, representation, 
		# iteration, equality testing and len()		
		if self.enable_row_factory:
			self.client.row_factory = sqlite3.Row
		
		# Immediately commit when make any modifications for database
		if self.enable_autocommit:
			self.client.isolation_level = None
		
		if hasattr(self.text_factory, '__call__'):
			self.client.text_factory = self.text_factory
		else:
			self.client.text_factory = str # sqlite3 default

		# Add custom Python functions to sqlite3
		for item in config['custom_functions']:
			if item[0] == 'function':
				self.add_function(item[1], item[2], item[3])
			elif item[0] == 'aggregate':
				self.add_aggregate(item[1], item[2], item[3])
			elif item[0] == 'collation':
				self.add_collation(item[1], item[2])

		# Add custom Python data types to sqlite3
		for datatype, typename, py2sqlite_func, sqlite2py_func in config['custom_types']:
			if datatype and py2sqlite_func:
				self.add_adapter(datatype, py2sqlite_func)
			if typename and sqlite2py_func:
				self.add_converter(typename, sqlite2py_func)

	def debug(self, msg, level='DEBUG'):
		now = datetime.datetime.now()
		if not self.enable_debug:
			pass
		else:
			print('[{}]'.format(self.debug_prefix), '[{}]'.format(level), '[{}]'.format(now), msg)
	
	def add_adapter(self, datatype, adapte_func):
		'''
		Registers a callable to convert the custom Python type into one of SQLite’s supported types.
		
		Another way to do this, is by defining method __conform__() in the datatype.
		'''
		if not datatype:
			return None
		if not hasattr(adapte_func, '__call__'):
			raise Exception('adapte function invalid')
		
		self.custom_types[datatype] = adapte_func
		sqlite3.register_adapter(datatype, adapte_func)

	def add_converter(self, typename, convert_func):
		'''
		Registers a callable to convert a bytestring from the database into a custom Python type.
		'''
		if not isinstance(typename, str):
			raise Exception('typename should be a string')
		if not hasattr(convert_func, '__call__'):
			raise Exception('convert function invalid')

		self.custom_types[typename] = convert_func
		sqlite3.register_converter(typename, convert_func)

	def add_function(self, func_name, num_params, func):
		'''
		Description:
		
		Add python callable object as a SQL function, you can 
		later use that python callable with func_name in your SQL statements.
		The func will accepts the number of num_params parameters
		
		Example:
		
		cursor.execute('SELECT func_name(?)', 'somthing to be passed')
		'''
		
		if not isinstance(func_name, str):
			raise Exception('argument func_name should be string')
		if not isinstance(num_params, int):
			raise Exception('argument num_params should be int')
		if not hasattr(func, '__call__'):
			raise Exception('argument func should be callable')
		
		self.client.create_function(func_name, num_params, func)

	def add_aggregate(self, func_name, num_params, cls):
		'''
		Description:

		Add python class as a SQL aggregate function, you can 
		later use that python class with func_name in your SQL statements.
		The python class must implement the following methods
			step() 		- accepts the number of num_params parameters
			finalize()	- return result of aggregate, should be bytes, str, int, float, or None
		
		Example:
		
		cursor.execute('SELECT func_name(?) FROM test')
		'''

		if not isinstance(func_name, str):
			raise Exception('argument func_name should be string')
		if not isinstance(num_params, int):
			raise Exception('argument num_params should be int')
		if not hasattr(cls, '__class__'):
			raise Exception('argument func should be class')
		
		self.client.create_aggregate(func_name, num_params, cls)

	def add_collation(self, coll_name, func):
		'''
		Description:

		Add python callable as SQL collate function, you can 
		later use that python class with func_name in your SQL 'ORDER BY ... COLLATE ...' statements.
		The func will accepts two bytestring, the return is just like cmp function
		
		Example:
		
		cursor.execute('SELECT username FROM user ORDER BY age COLLATE reverse')
		'''
		if not isinstance(coll_name, str):
			raise Exception('argument func_name should be string')
		if not hasattr(func, '__call__'):
			raise Exception('argument func should be callable')
		
		self.client.create_collation(coll_name, func)

	def total_changes(self):
		'''
		The total number of database rows that have been modified, 
		inserted, or deleted since the database connection was opened.
		'''
		return self.client.total_changes

	def get_connection(self):
		return self.client

	def execute(self, sql, params=None, autocommit=False):
		cursor = None
		if not params:
			cursor = self.client.execute(sql)
		else:
			cursor = self.client.execute(sql, params)
		if autocommit:
			self.commit()
		return cursor

	def executemany(self, sql, params, autocommit=False):
		cursor = self.client.executemany(sql, params)
		if autocommit:
			self.commit()
		return cursor

	def executescript(self, sql_statements, autocommit=False):
		cursor = self.client.executescript(sql_statements)
		if autocommit:
			self.commit()
		return cursor
	
	def commit(self):
		'''
		Commit current transaction, then your changes for the 
		database will be visible to other database connections.
		'''
		self.client.commit()

	def rollback(self):
		'''
		Rolls back any changes to the database since the last call to commit()
		'''
		self.client.rollback()

	def __del__(self):
		self.close()

	def close(self, commit=True):
		'''
		By default commit current trasaction and then close connection.
		'''
		if commit:
			self.commit()
		self.client.close()
	
	def cli(self, con):
		# cl = SimpleCl(con, copy.deepcopy(self.connection_args))
		# cl.run()
		run_cl_client(con)

	def dump(self, dump):
		with open(dump, 'w') as f:
			for line in self.client.iterdump():
				f.write('%s\n' % line)

	def validate_placeholder_in_sql(self, sql, params):
		sql = str(sql)
		if isinstance(params, tuple):
			placeholder = self.position_parameter_placeholder
			return len(sql.split(placeholder))-1 == len(params)
		elif isinstance(params, dict):
			flag = True
			for key in params:
				placeholder = self.keyword_parameter_placeholder.format(key)
				if sql.find(placeholder) == -1:
					flag = False
					break
			return flag
		return False
