#!/usr/bin/env python 
import string

def fix_loc(loc_string):
	out = loc_string.translate(string.maketrans("",""), string.punctuation).lower().strip()
	return out


f = open('sorted-locations.txt', 'r') 

for line in f:
	print fix_loc(line.replace('\n', ''))
