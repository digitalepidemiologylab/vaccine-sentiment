#!/usr/bin/env python 

import geocode
import csv	
import sys

if len(sys.argv) < 2:
	print "incorrect"
file_num = sys.argv[1]

in_file_name = "results/geocoded-" + file_num + '.txt' 
out_file_name = "results/geocoded-" + file_num + "-special.txt"

infile = csv.reader(open(in_file_name, 'r'), delimiter=';', quotechar='"')
outfile = csv.writer(open(out_file_name, 'w'), delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

for line in infile:
	if len(line) == 3 and line[-1] == 'unknown':

		user_name = line[0]
		location = line[1]

		if len(location) != len(location.strip()):
			location = location.strip()
			
		special = geocode.special_cases(location) 

		if special:
			if special.no_consensus:
				outfile.writerow([user_name, location, 'no_consensus'])
			elif special.ambiguous:
				outfile.writerow([user_name, location, 'ambiguous'])
			else:
				outfile.writerow([user_name, location, special.country_code, special.state_code])
		else:
			outfile.writerow([user_name, location, 'unknown'])
	else:
		outfile.writerow(line)
