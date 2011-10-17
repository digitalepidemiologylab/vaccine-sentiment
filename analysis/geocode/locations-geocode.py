#!/usr/bin/env python 

import geocode
import csv
import sys

if len(sys.argv) < 2:
	print "incorrect"

file_num = sys.argv[1] 
file_name = 'data/locs-' + file_num + '.txt'

out_file_name = 'results/geocoded-' + file_num + '.txt'

infile = csv.reader(open(file_name, 'r'), delimiter=';', quotechar='"')
outfile = csv.writer(open(out_file_name, 'w'), delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

for line in infile:
	user_name = line[0]
	location = line[1].replace('\n', '')

	result = geocode.extract_location(location)

	if result:
		if result.no_consensus:
			outfile.writerow([user_name, location, 'no_consensus'])
		elif result.ambiguous:
			outfile.writerow([user_name, location, 'ambiguous'])
		else:
			outfile.writerow([user_name, location, result.country_code, result.state_code])
	else:
		outfile.writerow([user_name, location, 'unknown'])
