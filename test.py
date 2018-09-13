import sqlite3

from quick_sqlite3.client import SimpleClient

client = SimpleClient(
	database=('dump.db')
)

# iteraction 
# db = sqlite3.connect('test.db')
# client.cli(db)

# method sql
# rows = client.sql('select * from email where id>=? and id<=?', (1, 3))
# for row in rows:
# 	print(row['subject'])

# method create_table
client.drop_table('users')
client.create_table('users', (('username', 's'), ('phone', 's')))
# client.cli(client.get_connection())

# method insert_table
client.insert_table('users', {'username': 'xiao', 'phone': '166'})
print(client.one_table('users', (('username', '="xiao"'),)))

# method drop_table
# client.drop_table('test')
# client.cli(client.get_connection())

# method count_table
# print(client.count_table('email', (('id', '>1'), ('id', '<3'))))

# method id_table
# row = client.id_table('email', 2)
# print(row['subject'])

# method one_table
# row = client.one_table('email', (('id', '>0'), ('id', '<3')), ('id desc',))
# print(row['subject'])

# method select_table
# for i in range(1, 4):
# 	rows = client.select_table(
# 		'email', 
# 		('id', 'subject'), 
# 		(('id', '>0'), ('id', '<30')), 
# 		('id desc',),
# 		(),
# 		page_nth=i,
# 		page_num=10)
# 	print('Page %d' % i)
# 	for row in rows:
# 		print(row['id'], row['subject'])

