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

		loc_words = location.split()
		no_stop_words = [w for w in loc_words if w.lower() not in geocode.LUCENE_STOP_WORDS] 

		#ON is a stop word, but also the two letter code for Ontario. We deal with it separately. 
		ontario_fix = False
		if ('ON' in loc_words) and (len(loc_words) - len(no_stop_words) == 1):
			ontario_fix = True
			
		if (len(location) != len(location.strip())) or ontario_fix:
			location = location.strip()
			print location
			
			special = geocode.extract_location(location) 

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
	else:
		outfile.writerow(line)
