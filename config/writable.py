import datetime

from ..helper import md5sum, strip, reverse_cmp, JoinAggregate, datetime_py2sqlite, datetime_sqlite2py

config = {
	
	'database': 'dump.db',
	
	'dump': 'dump.sql',
	
	'enable_debug': True,
	
	'enable_row_factory': True,
	
	'text_factory': lambda text: text.decode('utf8'),
	
	'waiting_unlock_timeout': 5,
	
	'cached_sql_statements': 100,
	
	'enable_autocommit': False,
	
	'custom_functions': [
		('function', 'md5sum', 1, md5sum),
		('function', 'strip', 1, strip),
		('aggregate', 'join', 1, JoinAggregate),
		('collation', 'reverse', reverse_cmp)
	],

	'custom_types': [
		(datetime.datetime, 'datetime', datetime_py2sqlite, datetime_sqlite2py)
	]
}

config_description = {
	
	'database': 'default database',
	
	'dump': 'When dump database with SQL format, will be written into the dump file',
	
	'enable_debug': 'Enable debug to display runtime information',
	
	'enable_row_factory': '''
		Enable row factory to support access by column name and index, representation, 
	 	iteration, equality testing and len().
	''',

	'text_factory': '''
		SQLite TEXT columns will be converted by text factory before return to 
		 result set. Accept a bytes as parameter.
	''',
	
	'waiting_unlock_timeout': '''
		When connect to database may wait other connections unlock(commit
		 trasaction) database util timeout.
	''',
	
	'cached_sql_statements': 'Cache statement to avoid SQL parsing overhead',
	
	'enable_autocommit': '''
		By default, sqlite3 implicitly opens trasaction before a Data Modification statements(
		 i.e. INSERT/UPDATE/DELETE) and implicitly commit trasaction before non-Data Modification 
		 and non-SELECT statement(i.e. CREATE).
		Enable autocommit to ensure every changes made for database are immediately written 
		 and visible by other connections(you should know that disabling autocommit gives you 
		 performance boost).
	''',

	'custom_functions': '''
		Custom python functions as SQLite inner function, aggregate and collation.
	''',

	'custom_types': '''
		Python None, int, float, str, bytes will be auto-converted into SQLite
		 NULL, INTEGER, REAL, TEXT, BLOB. 
		But other python custom types should has a **adapter** to auto convert into SQLite
		and when retrieve from database should use a **converter** to auto convert it back
		to corresponding python custom type. 
		Custom python data types auto convert into SQLite data types. list item is 
		tuple(datetype, typename, adapte_func, convert_func), everything in tuple is optional.
		**Notice** that adapte_func should return None, int, str, float, or bytes and convert_func should
		 return a datatype object.
	'''
}