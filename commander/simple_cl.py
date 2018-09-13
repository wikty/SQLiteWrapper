import sqlite3, copy, os, sys, re

from .utils import print_list_as_table

class SimpleCl(object):
	'''
	con -> this connection database will be loaded into memory
	con_kwargs -> use this connection arguments to connect the memory
	'''
	def __init__(self, con=None, con_kwargs=None):
		self._con = con if isinstance(con, sqlite3.Connection) else None
		self._con_kwargs = con_kwargs if isinstance(con_kwargs, dict) else {}
		self.con = None
		self.con_kwargs = None
		self.cur = None
		self.cached_statements = []
		self.current_statements = ''
		self.dump = 'dump.sql'

	def get_dump_file_name(self):
		dump = self.dump
		name, ext = dump.split('.')
		i = 0
		while os.path.exists(dump):
			i += 1
			dump = '.'.join(['{}-{}'.format(name, i), ext])
		return os.path.abspath(dump)

	def cache(self):
		self.cached_statements.append(self.current_statements)
		self.current_statements = ''

	def dump_interaction(self, dump_file):
		with open(dump_file, 'w', encoding='utf8') as f:
			f.write('\n'.join(self.cached_statements))

	def dump_database(self, dump_file):
		with open(dump_file, 'w', encoding='utf8') as f:
			for line in self.con.iterdump():
				f.write('%s\n' % line)

	def clean_database(self, con):
		for row in con.execute('SELECT name FROM sqlite_master WHERE type="table"'):
			tbl_name = row[0]
			con.execute('DORP TABLE IF EXISTS {}'.format(tbl_name))

	def run(self):
		print('Welcone to Sqlite3 Command Line Iteraction')
		self.con_kwargs = copy.deepcopy(self._con_kwargs)
		self.con_kwargs['database'] = ':memory:'
		self.con = sqlite3.connect(**self.con_kwargs)
		self.con.isolation_level = None # enable auto-commit mode
		self.con.text_factory = lambda item: item.decode('utf8')
		self.cur = self.con.cursor()

		if self._con:
			count = 0
			for line in self._con.iterdump():
				count += 1
				self.cur.execute(line)
			print('Load your database into memory and execute %d SQL statements' % count)

		print('Please type your SQL commands')
		print('(Enter exit or Ctrl+C to leave interaction):')
		try:
			while True:
				line = input('# ')
				if not line:
					continue
				if line.lower() == 'exit':
					raise KeyboardInterrupt()
				
				self.current_statements += line
				if not sqlite3.complete_statement(self.current_statements):
					continue

				try:
					for sql in [s.strip() for s in self.current_statements.split(';') if s.strip()]:
						statement = sql.split()[0].upper()
						if statement == 'SELECT':
							self.cur.execute(sql)
							column_names = [t[0] for t in self.cur.description]
							results = self.cur.fetchall()
							print_list_as_table(results, column_names)
						elif statement == 'INSERT':
							self.cur.execute(sql)
							lastrowid = self.cur.lastrowid
							print_list_as_table([lastrowid], ['Last Modified ID'])
						elif statement in set(['UPDATE', 'DELETE']):
							if not re.search(r'\s+WHERE\s+.+?=', sql.upper()):
								print("\nWaring! \nYour SQL statement doesn't have WHERE clause")
								r = input("continue(y/n)?")
								if not 'yes'.startswith(r.strip().lower()):
									continue
							self.cur.execute(sql)
							rowcount = self.cur.rowcount
							print_list_as_table([rowcount], ['Affected Row Count'])
				except Exception as e:
					print('Occured Errors: %s' % str(e))
					self.current_statements = ''
				else:
					self.cache()
		except KeyboardInterrupt:
			if self.cached_statements:
				dump_file = self.get_dump_file_name()
				print('\nSave your interaction into file: %s?' % dump_file)
				save_iteraction = True
				try:
					r = input('continue(y/n):')
					if not 'yes'.startswith(r.strip().lower()):
						raise KeyboardInterrupt()
				except KeyboardInterrupt:
					save_iteraction = False
				if save_iteraction:
					self.dump_interaction(dump_file)
			
			dump_file = self.get_dump_file_name()
			print('\nDump database into file: %s?' % dump_file)
			save_database = True
			try:
				r = input('continue(y/n):')
				if not 'yes'.startswith(r.strip().lower()):
					raise KeyboardInterrupt()
			except KeyboardInterrupt:
				save_database = False
			if save_database:
				self.dump_database(dump_file)
			sys.exit(0)