import sqlite3

config = {
	'basic_types': {
		'i': 'INTEGER',
		'f': 'REAL',
		's': 'TEXT',
		'b': 'BLOB',
		'n': 'NULL'
	},

	'position_parameter_placeholder': '?',

	'keyword_parameter_placeholder': ':{keyword}',
	
	'detect_types': sqlite3.PARSE_COLNAMES,

	'process_hander': (None, 0),

	'trace_callback': None
}

config_description = {
	'basic_types': '''
		type  	SQLite3 	Python
		i 	= 	INTEGER	<->  int
		f 	= 	REAL	<->  float
		s 	= 	TEXT  	<->  str(depend on text_factory, str is default)
		b 	= 	BLOB 	<->  bytes
		n 	= 	NULL 	<->  None
	''',

	'position_parameter_placeholder': '''
		execute() sencond argument should be a tuple
		cursor.execute(
			"insert into user(name, age) values (?, ?)", 
			(username, userage)
		)	
	''',

	'keyword_parameter_placeholder': '''
		execute() sencond argument should be a dict
		cursor.excute(
			'select * from user where age<:min_age and age>:_max_age and gender=:gender', 
			{'gender': 'f', 'min_age': 20, 'max_age': 30}
		)
	''',
	
	'detect_types': '''
		SQL like this: select column_name as "new_column_name [typename]" from test	
		cursor.execute('select p as "p [point]" from test')
	''',

	'process_hander': '''
		Registers a callback. The callback is invoked for every n instructions of the SQLite virtual machine
	''',

	'trace_callback': '''
		Registers trace_callback to be called for each SQL statement that is actually executed by the SQLite backend.
	'''
}