def welcome_txt():
	return 'Welcome to SQLite3 Iteraction!'

def leave_txt():
	return 'Goodbye...!'

def connect_database_txt(status, *args):
	if status == -1:
		s1 = ', '.join(['{0}={1}'.format(k, v) for k,v in args[0].items()])
		s2 = args[1]
		return '''Connect to database with parameters: {0}
Occured Errors: {1}'''.format(s1, s2)
	elif status == 1:
		s = ', '.join(['{0}={1}'.format(k, v) for k,v in args[0].items()])
		return 'Connect to database with parameters: {0}'.format(s)

def load_database_txt(status, *args):
	if status == -1:
		return 'Please connect to database first!'
	elif status == -2:
		return 'There is no database to be loaded!'
	elif status == -3:
		return 'When loading database, Occured Errors: {0}'.format(args[0])
	elif status == 1:
		return 'Load database into memory and execute {0} SQL statements'.format(args[0])

def dump_database_txt(status, *args):
	if status == -1:
		return 'Please connect to database first!'
	elif status == -2:
		return 'The dump file [{0}] exists, cannot overwrite it!'.format(args[0])
	elif status == -3:
		return 'When dumping database, Occured Errors: {0}'.format(args[0])
	elif status == 1:
		return 'Dump database into [{0}] file'.format(args[0])

def show_database_txt(status, *args):
	if status == -1:
		return 'Please connect to database first!'
	elif status == -2:
		return 'When showing database, Occured Errors: {0}'.format(args[0])
	elif status == -3:
		return 'No Table named [{0}]'.format(args[0])
	elif status == 1:
		return '''Database Tables: 
{0}'''.format(args[0])
	elif status == 2:
		return '''Database Table [{0}]
{1}'''.format(args[0], args[1])

def command_help_txt(status, *args):
	t = '''{cmd:<10}
    Description: {description}
    Usage:       {usage}'''
	if status == 1:
		return t.format(cmd=args[0], description=args[1], usage=args[2])
	elif status == 2:
		l = []
		for cmd, description, usage in args[0]:
			l.append(t.format(cmd=cmd, description=description, usage=usage))
		return '\n'.join(l)
	elif status == -1:
		return 'Invalid command [{0}]'.format(args[0])

def command_load_txt(status, *args):
	if status == -1:
		return 'database file [{0}] not exists'.format(args[0])
	elif status == -2:
		return 'When loading database, Occured Errors: {0}'.format(args[0])
	elif status == -3:
		return 'Invalid Command [{0}]'.format(args[0])

def command_dump_txt(status, *args):
	if status == -1:
		return 'The dump file [{0}] exists, cannot overwrite it!'.format(args[0])
	elif status == -2:
		return 'Invalid Command [{0}]'.format(args[0])

def command_exit_txt(status, *args):
	if status == 1:
		return 'Goodbye!'

def command_show_txt(status, *args):
	if status == -1:
		return 'Invalid Command [{0}]'.format(args[0])

def lock_question_txt(status, *args):
	if status == 1:
		return 'Do you want dump your interaction?(y/n)'

def execute_statements_txt(status, *args):
	if status == -1:
		return 'The statements does not terminated with a semicolon'
	elif status == -2:
		return 'When executing statements, Occured Errors: {0}'.format(args[0])