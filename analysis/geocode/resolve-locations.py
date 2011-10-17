#!/usr/bin/env python 

#We've already geo-coded each unique user, location pair. Now we consolidate those 
#into a single location for the user (if possible). If the user can't be resolved to a 
#single location, we place all the user, location entries into a duplicates file, 
#so that those can be resolved manually.

import sys
import csv
import MySQLdb
from database_settings import DATABASES

class Location:
	country_code = None
	state_code = None
	location_string = None
	user_name = None
	unknown = False 
	known = False
	ambiguous = False
	unresolved_duplicates = False 

def resolve_locations(all_for_user):
	location = Location()

	for l in all_for_user:
		location_string = l[1]

		if len(l) == 3 and l[-1] == 'unknown' and not location.known:
			location.unknown = True 
			if len(location_string) > 1:
				location.location_string = location_string
		if len(l) == 3 and l[-1] == 'ambiguous' and not location.known:
			location.ambiguous = True
			location.unknown  = True
			if len(location_string) > 1:
				location.location_string = location_string
		if len(l) == 4:	
			country = l[2]
			state = l[3]

			location.known = True

			if location.unknown:
				location.unknown = False
				location.ambiguous = False
				location.country_code = country
				location.state_code = state
				location.location_string = location_string
			elif location.country_code is None:
				location.country_code = country
				location.state_code = state
				location.location_string = location_string
			elif not (location.country_code == country or location.state_code == state):
				location.unresolved_duplicates = True
				return location
	return location

if len(sys.argv) < 2:
	print "incorrect"

file_num = sys.argv[1]
file_name = 'results/geocoded-' + file_num + '.txt'

dups_file = csv.writer(open('duplicates.csv', 'a'), delimiter=';', 
					quotechar='"', quoting=csv.QUOTE_ALL)

infile = csv.reader(open(file_name, 'r'), delimiter=';', quotechar='"')

conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
			user=DATABASES['default']['USER'], 
			passwd=DATABASES['default']['PASSWORD'], 
			db=DATABASES['default']['NAME'])

cursor = conn.cursor()

current_user = None
all_rows = list(infile)
for x in all_rows:
	if len(x) !=3 and len(x) != 4:
		print x

	if x[0] != current_user:
		#Let's not process a user we've already seen before
		current_user = x[0]
		all_for_user = [y for y in all_rows if y[0] == current_user]

		location = resolve_locations(all_for_user)

		sql = ""
		if location.unresolved_duplicates == True:
			for l in all_for_user:
				dups_file.writerow(l)
		else:
			if location.ambiguous:
				sql = "UPDATE tweeter_tweeter SET unknown_location = 1, ambiguous_location = 1"
				if not location.location_string is None and len(location.location_string) > 0:
					sql += ", location_string='%s'" % conn.escape_string(location.location_string)
				sql += " WHERE user_name='%s'" % current_user
			elif location.unknown:
				#mark location as unknown
				sql = "UPDATE tweeter_tweeter SET unknown_location = 1, ambiguous_location = 0"
				if not location.location_string is None and len(location.location_string) > 0:
					sql += ", location_string='%s'" % conn.escape_string(location.location_string)
				sql += " WHERE user_name='%s'" % current_user
			else:
				sql = "UPDATE tweeter_tweeter SET location_string='%s', country_code='%s', state_code='%s', " % (
						conn.escape_string(location.location_string), location.country_code, location.state_code)
				sql +=" unknown_location = 0, ambiguous_location = 0, "
				sql += "location_count=%d WHERE user_name='%s'" % (len(all_for_user), current_user)

			#write sql to database
			if sql is None or sql == "":
				print current_user

			print sql
			cursor.execute(sql)

#clean up
cursor.close()
conn.commit()
conn.close()
