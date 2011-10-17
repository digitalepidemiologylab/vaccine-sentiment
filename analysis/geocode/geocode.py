#!/usr/bin/env python 

import urllib
import simplejson as json
import csv

from database_settings import YAHOO_APP_ID
YAHOO_GEOCODER_URL = 'http://where.yahooapis.com/geocode'

#These are identifiers that sometimes preprend lat, long strings
REVERSE_IDENTIFIERS = ['\xc3\x9cT:', 'iPhone:']

#These stop words taken from Lucene's StopAnalyzer.java class. 
#Extra word: 'here' added, because strangely enough this resolves to somewhere in 
#India.
LUCENE_STOP_WORDS = [
	'a', 'and', 'are', 'as', 'at', 
	'be', 'but', 'by', 'for', 'if', 
	'in', 'into', 'is', 'it', 'no', 'not', 
	'of', 'on', 'or', 'such', 'that', 'the',
	'their', 'then', 'there', 'these', 'they', 
	'this', 'to', 'was', 'will', 'with', 'here',
]

def yahoo_geocode(location):
	"Take a location, return the geographical location, if found"
	url_str = urllib.urlencode({
					'appid':YAHOO_APP_ID,
					'flags':'j',
					'q':location, 
				})

	s =  YAHOO_GEOCODER_URL + '?%s' % url_str
	f = urllib.urlopen(s) 
	json_result = json.loads(f.read())

	geocode_result = Geocode()

	if json_result['ResultSet']['Found'] > 0:
		if len(json_result['ResultSet']['Results']) > 1:
			geocode_result.ambiguous = True
		else:
			result = json_result['ResultSet']['Results'][0]

			geocode_result.country_code = result['countrycode']
			geocode_result.state_code = result['statecode']
			geocode_result.latitude = result['latitude']
			geocode_result.longitude = result['longitude']

		return geocode_result
	else:
		return None

def remove_stop_words(location):
	""" Remove stop words from the location string. We need to remove stop
	words and try because strings like 'Born in Texas' resolve to Texas,l
	Indiana (IN). Yes, there is a town in Indiana called Texas. """

	loc_words = location.split()
	no_stop_words = [w for w in loc_words if w.lower() not in LUCENE_STOP_WORDS]
	return " ".join(no_stop_words)

def yahoo_reverse_geocode(location):
	"Take a lat/long pair, and return the geographical location"
	url_str = urllib.urlencode({
			'appid':YAHOO_APP_ID,
			'flags':'j',
			'gflags':'R',
			'q':location, 
		})
	
	s = YAHOO_GEOCODER_URL + '?%s' % url_str
	f = urllib.urlopen(s)

	json_result = json.loads(f.read())

	geocode_result = Geocode()

	if json_result['ResultSet']['Found'] == 1:
		if len(json_result['ResultSet']['Results']) > 1:
			geocode_result.ambiguous = True
		else:
			result = json_result['ResultSet']['Results'][0]

			geocode_result.country_code = result['countrycode']
			geocode_result.state_code = result['statecode']
			geocode_result.latitude = result['latitude']
			geocode_result.longitude = result['longitude']
		return geocode_result
	else:
		return None

def strip_reverse_identifiers(location):
	"Location strings can contain identifiers before lat/long strings. Strip those out."
	loc_words = location.split()
	no_rev_ids = [w for w in loc_words if w not in REVERSE_IDENTIFIERS]
	return " ".join(no_rev_ids)

class Geocode:
	"Class to hold the results of the Geocoding process"
	country_code = None
	state_code = None
	latitude = None
	longitude = None

	#If there were multiple results returned from the geocoding
	#process, mark this as true. 
	ambiguous = False

	#If there is no consensus between successive geocoding runs, 
	#mark this as true
	no_consensus = False

def geocode_result_matches(gcl, gcr):
	return ((gcl.country_code == gcr.country_code) and (gcl.state_code == gcr.state_code) and (gcl.ambiguous == gcr.ambiguous) and (gcl.ambiguous == False))


def simple_geocode_location(location):
	"Just geocode the string. No processing on our end."
	return yahoo_geocode(location)

def special_cases(location):
	""" Because of our stop words logic, locations in Indiana (IN), Oregon (OR), and 
	The Netherlands don't resolve correctly. This attempts to fix that wrong"""
	loc_words = location.split()
	no_stop_words = [w for w in loc_words if w.lower() not in LUCENE_STOP_WORDS] 

	result = None
	if ('IN' in loc_words or 'OR' in loc_words or 'ON' in loc_words) and (len(loc_words) - len(no_stop_words) == 1):
		result = yahoo_geocode(location)
	elif (location.lower().find("the netherlands") > 0):
		result = yahoo_geocode(location)
	return result;

def special_ambiguous_cases(location):
	""" Two locations seem to resolve to multiple ones that we've noticed: New Delhi and Dubai. 
	We fix those locations, because they don't really have multiples. """	
	no_stop_words = remove_stop_words(location)

	result = None
		
	if (len(location) == len(no_stop_words)):
		if "dubai" in location.lower():
			result = Geocode()
			result.country_code="AE"
		elif "new delhi" in location.lower():
			result = Geocode()
			result.country_code = "IN"
			result.state_code = "DL"
	return result

def strict_geocode_location(location):
	"""Location strings that contain stop words are generally unreliable (based on experience), 
	so we don't geocode those locations"""
	no_stop_words = remove_stop_words(location)

	if (len(location) != len(no_stop_words)):
		special = special_cases(location)

		if special:
			return special
		else:
			result = Geocode()
			result.no_consensus = True
			return result
	else:
		result = yahoo_geocode(location)
		if result and result.ambiguous:
			sa = special_ambiguous_cases(location)

			if sa:
				result = sa
		return result

def geocode_location(location):
	""" Attempts to Geocode the location. Removes stop words and geocodes again. 
	If both results match, this considers the match a success. """
	result = yahoo_geocode(location)

	if result is not None:
		if result.ambiguous == True:
			return result
		else:
			#now remove the stop words, and try again
			no_stop_words = remove_stop_words(location)
			nsw_result = yahoo_geocode(no_stop_words)

			if nsw_result is not None:
				if geocode_result_matches(result, nsw_result):
					return result
				else:
					result.no_consensus = True
					return result
	return None

def reverse_geocode_location(location):
	""" Try to reserve geocode the location. Removes any extraneous known identifiers, 
	and reverse geocodes the remainder """
	no_stop_words = remove_stop_words(location)
	result = yahoo_reverse_geocode(strip_reverse_identifiers(no_stop_words))

	if result is not None:
		if result.ambiguous == False:
			return result
	return None

def extract_location(location):
	""" Given a string, try an extract a location. """
	if len(location) < 1:
		return None
		
	#If you don't remove leading and trailing spaces, the geocoding doesn't work
	location = location.strip()
	result = strict_geocode_location(location)

	if result is not None:
		if result.no_consensus:
			return None
		else:
			return result	
	else:
		result = reverse_geocode_location(location)
		if result is not None:
			return result
	return None

