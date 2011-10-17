#!/usr/bin/env python 

import sys;
import urllib;


if (len(sys.argv) < 2):
    log = sys.stdin;
else:
    logToRead = sys.argv[1];
    log = open(logToRead, "r");

for x in log.readlines():
	y = x.replace("&quot;", '"');
	print y;
