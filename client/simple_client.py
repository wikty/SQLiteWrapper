from .base_client import BaseClient

class SimpleClient(BaseClient):

	def __init__(self, **kwargs):
		super(SimpleClient, self).__init__(**kwargs)

	def script(self, sql_statements, autocommit=True):
		'''
		execute multiple sql statements.
		'''
		cursor = self.client.executescript(sql_statements, autocommit)

	def sql(self, sql, params, autocommit=True):
		'''
		Parameters:

			sql 
				sqlite3 module supports two kinds of placeholders
				cur.execute("insert into people values (?, ?)", (who, age))
				cur.execute("select * from people where name_last=:who and age=:age", {"who": who, "age": age})
		
			params
				None, tuple, dict, Iterator, Generator

		Return:

			SELECT 			-> result set list
			INSERT 			-> lastrowid
			UPDATE|DELETE 	-> affected row count
			else			-> affected row count
		'''
		cursor = None
		if not params:
			cursor = self.execute(sql, None, autocommit)
		if isinstance(params, tuple) or isinstance(params, list) or isinstance(params, dict):
			cursor = self.execute(sql, params, autocommit)
		elif hasattr(params, '__iter__'):
			# params is Iterator or Generator
			cursor = self.executemany(sql, params, autocommit)
		else:
			raise Exception('sql parameters invalid')
		
		sql_upper = sql.upper().strip()
		if sql_upper.startswith('SELECT'):
			return cursor.fetchall()
		elif sql_upper.startswith('INSERT'):
			return cursor.lastrowid
		else:
			# UPDATE|DELETE|Others
			return cursor.rowcount

	def create_table(self, tbl_name, columns, with_id_primary_key=True):
		'''
		Parameters:

			with_id_primary_key = True -> add id column as table's primary key
			columns = ((column_name, column_type, [column_constraint])) -> column definitions

			Avaiable column types(default TEXT)
			   type  	SQLite3 	Python
				i 	= 	INTEGER	<->  int
				f 	= 	REAL	<->  float
				s 	= 	TEXT  	<->  str(depend on text_factory, str is default)
				b 	= 	BLOB 	<->  bytes
				n 	= 	NULL 	<->  None

			Avaiable column constraints
				NOT NULL    -> the associated column may not contain a NULL value
				UNIQUE      -> each row must contain a unique combination of values in the columns identified by the UNIQUE constraint. 
		'''
		column_definitions = []
		if with_id_primary_key:
			column_definitions.append('id INTEGER PRIMARY KEY AUTOINCREMENT')
		for column in columns:
			column_name = column[0]
			column_type = self.basic_types.get(column[1], 'TEXT')
			column_constraint = '' if len(column) == 2 else column[2]
			if not (column_constraint.upper() in ['NOT NULL', 'UNIQUE']):
				column_constraint = ''
			col_def = '{} {} {}'.format(column_name, column_type, column_constraint).strip()
			column_definitions.append(col_def)
		
		sql = 'CREATE TABLE IF NOT EXISTS {table} ({columns});'.format(
			table=tbl_name, 
			columns=', '.join(column_definitions))
		
		self.debug(sql)
		self.execute(sql)
		self.commit()

	def drop_table(self, tbl_name):
		sql = 'DROP TABLE IF EXISTS {table}'.format(table=tbl_name)
		self.debug(sql)
		self.execute(sql)
		self.commit()

	def count_table(self, tbl_name, where_condition=()):
		'''
		where_condition = (('age', '50', '>'))
		'''
		params = []
		if where_condition:
			items = []
			for name, value, op in where_condition:
				items.append(name+op)
				params.append(value)
			where = ' and '.join(items)
			sql = 'SELECT COUNT(*) FROM {table} WHERE {where}'.format(table=tbl_name, where=where)
		else:
			sql = 'SELECT COUNT(*) FROM {table}'.format(table=tbl_name)
		
		self.debug(sql)
		cursor = self.execute(sql, params)
		result = cursor.fetchone()
		return result[0] if result else 0

	def id_table(self, tbl_name, item_id):
		sql = 'SELECT * FROM {table} WHERE id=?'.format(table=tbl_name)
		self.debug(sql)
		cursor = self.execute(sql, (item_id,))
		return cursor.fetchone()

	def one_table(self, tbl_name, where_condition=(), orderby=()):
		'''
		where_condition = (('id', '>30'))
		orderby = ('username', 'age')
		'''
		sql = 'SELECT * FROM {table}'.format(table=tbl_name)
		if where_condition:
			where = ' and '.join([name+condition for name, condition in where_condition])
			sql += ' WHERE {where}'.format(where=where)
		if orderby:
			sql += ' ORDER BY {}'.format(', '.join(orderby))
		sql += ' LIMIT 1'

		self.debug(sql)
		cursor = self.execute(sql)
		return cursor.fetchone()

	def select_table(self, 
		tbl_name, 
		columns=(), 
		where_condition=(), 
		orderby=(), 
		groupby=(), 
		page_nth=-1, 
		page_num=-1):
		'''
		columns = ((col_name1, typename), (col_name2, typename) ...)
		where_condition = (('id', '>30'))
		orderby = ('username', 'age')
		page_nth = 1 and page_num = 10 -> first 10 rows
		'''
		if columns:
			s = []
			for column in columns:
				if isinstance(column, tuple):
					s.append('{column} AS "{column} [typename]"'.format(column=column[0], typename=[column[1]]))
				else:
					s.append(column)
			sql = 'SELECT {columns} FROM {table}'.format(columns=', '.join(columns), table=tbl_name)
		else:
			sql = 'SELECT * FROM {table}'.format(table=tbl_name)

		if where_condition:
			sql += ' WHERE {}'.format(' and '.join([name+condition for name, condition in where_condition]))
		if groupby:
			sql += ' GROUP BY'.format(', '.join(groupby))
		if orderby:
			sql += ' ORDER BY {}'.format(', '.join(orderby))
		if page_num > 0 and page_nth > 0:
			limit = page_num
			offset = (page_nth-1)*page_num
			sql += ' LIMIT {limit} OFFSET {offset}'.format(limit=limit, offset=offset)

		self.debug(sql)
		cursor = self.execute(sql)
		return cursor.fetchall()

	def insert_table(self, tbl_name, columns={}):
		'''
		columns = {'fieldname': 'value'}
		'''
		sql = 'INSERT INTO {table} ({keys}) VALUES ({values})'.format(
			table=tbl_name,
			keys= ', '.join(columns.keys()),
			values=', '.join(['?']*len(columns.keys()))
		)
		
		self.debug(sql)
		cursor = self.execute(sql, list(columns.values()))
		return cursor.lastrowid

	def update_table(self, tbl_name, columns, where_condition=()):
		'''
		columns = {
			'field_name': 'field_value', # assign to the field
			'field_name': '++field_value' # add into the field
		}
		where_condition = (('id', '>30'))
		'''
		s = []
		for field_name, field_value in columns.items():
			field_name = str(field_name)
			field_value = str(field_value)
			if field_value.startswith('++'):
				s.append(field_name+'='+field_name+'+'+field_value[2:])
			else:
				s.append(field_name+'='+field_value)
		
		sql = 'UPDATE {table} SET {columns}'.format(
			table=tbl_name,
			fields=' '.join(s)
		)
		
		if where_condition:
			sql += ' WHERE {}'.format(' and '.join([name+condition for name, condition in where_condition]))

		self.debug(sql)
		cursor = self.execute(sql)
		return cursor.rowcount