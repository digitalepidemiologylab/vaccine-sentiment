#!/usr/bin/env python 

import csv
import geocode

#Create csv files (from the location file), each of 3000 entries. 
#3000 locations per run is a small enough chunk, ensuring that 
#we don't hit the geocode server too hard, and that a single 
#run of the geocode program does not fail from running too long. 


locations = csv.reader(open('unique-locations.csv'), delimiter=';', quotechar='"');

count = 0
for line in locations:
	if count % 3000 == 0:
		file_num = count / 3000
		file_name = 'data/locs-' + repr(file_num) + '.txt'
		outfile = csv.writer(open(file_name, 'w'), delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

	user_name = line[0]
	location = line[1].replace('\n', '')

	outfile.writerow([user_name, location])
	count += 1
