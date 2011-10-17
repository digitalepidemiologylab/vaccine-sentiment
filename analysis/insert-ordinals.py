import MySQLdb
from database_settings import DATABASES

#We assign each tweet in the database an ordinal from 1 to n in a randomized fashion. 
#The ordinals help ensure that every other tweet each rater gets is the same.

#connect to the database
conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
			user=DATABASES['default']['USER'], 
			passwd=DATABASES['default']['PASSWORD'], 
			db=DATABASES['default']['NAME'])
cursor = conn.cursor()

f = open('ids-randomized.txt', 'r')

count = 1
for l in f:
	l = l.replace('\n', '')
	sql = "UPDATE tweets_tweet SET ordinal=" + str(count) + " WHERE tweet_id=" + str(l)
	cursor.execute(sql)
	count += 1

#clean up
cursor.close()
conn.commit()
conn.close()
