import sqlite3, json, copy, os

from .cl_feedbacks import *

class ClCommander():
	default_response = {
		'header': {
			'status': 'ok', # avaiable status: ok, error
			'type': 'message', # avaiable type: message, data, termination
		},
		'body': ''
	}

	commands = {
		'EXIT': {
			'description': 'Leave interaction.',
			'usage': 'EXIT [nodump]'
		},
		'LOAD': {
			'description': 'Load a database into interaction.',
			'usage': 'LOAD <path_to_database_file>'
		},
		'DUMP': {
			'description': 'Dump iteraction with SQL format into a file.',
			'usage': 'DUMP <path_to_dump_file>'
		},
		'SHOW': {
			'description': 'Show database information.',
			'usage': 'SHOW table [<table-name>]'
		},
		'HELP': {
			'description': 'Query avaiable commands.',
			'usage': 'HELP [<command>]'
		}
	}

	def __init__(self, dump):
		self.con = None
		self.con_kwargs = None
		self.statements = ''
		self.cached_statements = []
		self.nodump = False

		self.dump = dump
		if dump:
			dirname = os.path.dirname(dump) or os.getcwd()
			if os.path.exists(dump) or not(os.access(dirname, os.W_OK)):
				raise Exception('Please specify a valid dump file location!')
		else:
			self.nodump = True

	def open(self, con=None, con_kwargs=None):
		con = con if con else None
		con_kwargs = con_kwargs if con_kwargs else {}
		msg = []
		msg.append(welcome_txt())
		# connect database
		r = self.connect_database(con_kwargs)
		msg.append(self.get_body(r))
		# load database
		if self.is_ok_status(r) and con:
			r = self.load_database(con)
			msg.append(self.get_body(r))
		
		if self.is_ok_status(r):
			return self.message('ok', '\n'.join(msg))
		else:
			return self.message('error', '\n'.join(msg))

	def close(self):
		if not self.nodump:
			return self.dump_database(self.dump)
		else:
			return self.message('ok', command_exit_txt(1))

	def connect_database(self, con_kwargs=None):
		try:
			self.con_kwargs = {} if not con_kwargs else copy.deepcopy(con_kwargs)
			self.con_kwargs['database'] = ':memory:'
			self.con = sqlite3.connect(**self.con_kwargs)
			self.con.isolation_level = None # enable auto-commit mode
			self.con.text_factory = lambda item: item.decode('utf8')
		except Exception as e:
			return self.message('error', connect_database_txt(-1, self.con_kwargs, str(e)))
		
		return self.message('ok', connect_database_txt(1, self.con_kwargs))

	def load_database(self, con):
		if not self.con:
			return self.message('error', load_database_txt(-1))
		if not con:
			return self.message('error', load_database_txt(-2))
		try:
			count = 0
			with self.con:
				# automatically commit or rollback transactions
				for sql in con.iterdump():
					count += 1
					self.con.execute(sql)
		except Exception as e:
			return self.message('error', load_database_txt(-3, str(e)))
		
		return self.message('ok', load_database_txt(1, count))

	def dump_database(self, dump):
		if not self.con:
			return self.message('error', dump_database_txt(-1))
		if os.path.exists(dump):
			return self.message('error', dump_database_txt(-2, dump))
		try:
			with open(dump, 'w', encoding='utf8') as f:
				for sql in self.con.iterdump():
					f.write('%s\n' % sql)
		except Exception as e:
			return self.message('error', dump_database_txt(-3, str(e)))
		return self.message('ok', dump_database_txt(1, dump))

	def show_database(self, tbl_name=None):
		if not self.con:
			return self.message('error', show_database_txt(-1))
		try:
			if not tbl_name:
				results = self.con.execute('SELECT name FROM sqlite_master WHERE type="table"')
				results = [item[0] for item in results]
				results = ' | '.join(results).strip()
			else:
				results = self.con.execute('SELECT sql FROM sqlite_master WHERE type="table" and name=?', (tbl_name,))
				results = [item[0] for item in results]
				results = ' '.join(results).strip()
		except Exception as e:
			return self.message('error', show_database_txt(-2, str(e)))
		if not tbl_name:
			return self.message('ok', show_database_txt(1, results))
		elif results:
			return self.message('ok', show_database_txt(2, tbl_name, results))
		else:
			return self.message('error', show_database_txt(-3, tbl_name))
			

	def is_ok_status(self, response):
		return response['header']['status'] == 'ok'

	def get_body(self, response):
		return response['body']

	def execute_command(self, raw_cmd, cmd, args):
		nargs = len(args)
		if cmd == 'HELP':
			if nargs == 1:
				a = args[0].upper()
				if a in self.commands:
					return self.message('ok', command_help_txt(1, a, self.commands[a]['description'], self.commands[a]['usage']))
				else:
					return self.message('error', command_help_txt(-1, raw_cmd))
			cmds = [(cmd, self.commands[cmd]['description'], self.commands[cmd]['usage']) for cmd in self.commands]
			return self.message('ok', command_help_txt(2, cmds))
		
		elif cmd == 'LOAD':
			if nargs == 1:
				a = args[0]
				if not os.path.exists(a):
					return self.message('error', command_load_txt(-1, a))
				try:
					con = sqlite3.connect(a)
				except Exception as e:
					return self.message('error', command_load_txt(-2, str(e)))
				else:
					return self.load_database(con)	
			return self.message('error', command_load_txt(-3, raw_cmd))
		
		elif cmd == 'DUMP':
			if nargs == 1:
				a = args[0]
				if os.path.exists(a):
					return self.message('error', command_dump_txt(-1, a))
				return self.dump_database(a)
			return self.message('error', command_dump_txt(-2, raw_cmd))
		
		elif cmd == 'SHOW':
			if nargs == 1:
				a = args[0].strip().lower()
				if a == 'table':
					return self.show_database()
			if nargs == 2:
				a = args[0].strip().lower()
				if a == 'table':
					return self.show_database(args[1])
			return self.message('error', command_show_txt(-1, raw_cmd))

		elif cmd == 'EXIT':
			if nargs == 1:
				a = args[0].strip().lower()
				if a == 'nodump':
					self.nodump = True
			return self.termination('ok', command_exit_txt(1))

	
	def cache_statements(self):
		self.cached_statements.append(self.statements)
		self.clean_statements()

	def clean_statements(self):
		self.statements = ''

	def execute_statements(self, statements):
		self.statements += statements
		if not sqlite3.complete_statement(self.statements):
			return self.message('error', execute_statements_txt(-1))
		
		statements = self.statements
		self.cache_statements()
		try:
			results = []
			for sql in [s.strip() for s in statements.split(';')]:
				cursor = self.con.execute(sql)
				sql_upper = sql.upper()
				if sql_upper.startswith('SELECT'):
					column_names = [c[0] for c in cursor.description]
					results.append(column_names)
					results.extend(cursor.fetchall())	
				elif sql_upper.startswith('INSERT'):
					results.append([cursor.lastrowid])
				else:
					results.append([cursor.rowcount])
		except Exception as e:
			return self.message('error', execute_statements_txt(-2, str(e)))
		return self.data(results)

	def message(self, status, msg):
		return self.response(msg, {
			'type': 'message',
			'status': status
		})

	def data(self, results):
		return self.response(results, {
			'type': 'data',
			'status': 'ok'
		})

	def termination(self, status, msg):
		return self.response(msg, {
			'type': 'termination',
			'status': status
		})

	def response(self, body=None, header=None):
		if not header:
			header = self.default_response.get('header', {})
		if not body:
			body = self.default_response.get('body', '')
		return {
			'header': header,
			'body': body
		}

	def parse_command(self, s):
		args = str(s).strip().strip(';').split()
		cmd = args[0].strip().upper()
		if cmd not in self.commands:
			return (None, None)
		return (cmd, args[1:])

	def accept(self, s):
		cmd, args = self.parse_command(s)
		if cmd:
			self.clean_statements()
			r = self.execute_command(s, cmd, args)
		else:
			r = self.execute_statements(s)
		return r