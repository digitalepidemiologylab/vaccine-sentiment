#!/usr/bin/env python 

import MySQLdb
import string
from database_settings import DATABASES

#Find similar locations to the one you have already resolved. Resolve those the same way. 

class SQLStatements:
	AUTO_GEOCODER_ID = 72
	
	TRAINING_SQL = "SELECT location_string, country_code, state_code, unknown_location" 
	TRAINING_SQL += " FROM tweeter_tweeter WHERE human_geocoder_id IS NOT NULL AND ambiguous_location=0"
	TRAINING_SQL += " AND human_geocoder_id != %s" % AUTO_GEOCODER_ID 

	SIMILAR_SQL = "SELECT id, location_string FROM tweeter_tweeter WHERE location_string LIKE '%%%s%%' AND unknown_location=1 AND human_geocoder_id is NULL and ambiguous_location=0"

	UPDATE_NO_LOC = "UPDATE tweeter_tweeter SET unknown_location=1, ambiguous_location=0, human_geocoder_id=%s" % AUTO_GEOCODER_ID 
	UPDATE_NO_LOC += " WHERE id=%s"

	UPDATE_LOC = "UPDATE tweeter_tweeter SET unknown_location=0, ambiguous_location=0, country_code='%s', state_code='%s', "
	UPDATE_LOC += " human_geocoder_id=" + repr(AUTO_GEOCODER_ID)
	UPDATE_LOC += " WHERE id=%s"

def fix_loc(loc_string):
	out = loc_string.translate(string.maketrans("",""), string.punctuation).lower()
	return out

def unique(rows):
	row_set = {}

	for row in rows:
		(location, country, state, unknown_location) = row
		loc_str = fix_loc(location)
		if loc_str not in row_set:
			row_set[loc_str] = (loc_str, country, state, unknown_location)

	return row_set.values()

def get_training_data(conn):
	cursor = conn.cursor()

	cursor.execute(SQLStatements.TRAINING_SQL)
	rows = list(cursor.fetchall())

	return unique(rows)
	cursor.close()

def get_similar_locations(location_string, conn):
	cursor = conn.cursor()
	sql = SQLStatements.SIMILAR_SQL % location_string

	cursor.execute(sql)
	rows = cursor.fetchall()

	similar = []

	for row in rows:
		(id, loc_string) = row
		fixed_loc_string = fix_loc(loc_string)
		if fixed_loc_string == location_string:
			similar.append(id)

	return similar
	cursor.close()

def update_similar_locations(similar_locations, location_info, conn):
	cursor = conn.cursor()
	(location_string, country_code, state_code, unknown_location) = location_info 

	for l in similar_locations:
		sql = None
		if unknown_location == 1:
			sql = SQLStatements.UPDATE_NO_LOC % l
		else:
			sql = SQLStatements.UPDATE_LOC % (country_code, state_code, l)
		#print sql
		cursor.execute(sql)

	conn.commit()
	cursor.close()

def locate_rest(train_data, conn):
	for td in train_data:
		(location_string, country_code, state_code, unknown_location) = td
		similar_locations = get_similar_locations(location_string, conn)
		if len(similar_locations) > 1:
			update_similar_locations(similar_locations, td, conn)

def main_function():
	conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
			user=DATABASES['default']['USER'], 
			passwd=DATABASES['default']['PASSWORD'], 
			db=DATABASES['default']['NAME'])
	train_data = get_training_data(conn)
	locate_rest(train_data, conn)

if __name__ == '__main__':
	main_function()
