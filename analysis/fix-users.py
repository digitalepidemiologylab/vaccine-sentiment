#!/usr/bin/env python 

#In the original file there are users with twitter_user_id=0 (they show up twice). The incorrect-dup-users.txt file 
#contains the Twitter user names. We remove those users from the database. 

import MySQLdb
from database_settings import DATABASES

conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
			user=DATABASES['default']['USER'], 
			passwd=DATABASES['default']['PASSWORD'], 
			db=DATABASES['default']['NAME'])

f = open('incorrect-dup-users.txt', 'r')

cursor = conn.cursor()

for line in f:
	user_name = line.replace('\n', '')

	SQL = "SELECT id FROM tweeter_tweeter where user_name='%s' AND twitter_user_id = 0" % user_name
	cursor.execute(SQL)

	rows = cursor.fetchall()
	user_id = rows[0][0]

	DELETE_SQL = "DELETE FROM tweeter_tweeter where user_name='%s' AND id=%s" % (user_name, user_id)
	cursor.execute(DELETE_SQL)

conn.commit()
cursor.close()
