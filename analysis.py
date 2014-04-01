#!/usr/bin/env python

# import requests
import os
import time
from pfs_service_dropbox import *
# from pfs_service_dropbox import pfs_service_dropbox, pfs_file_dropbox

def test1(service, filename):
	service.open(filename,"w+")
	then = time.clock()
	service.write(filename,"HELLO THERE SIR")
	service.close(filename)
	service.exit()
	now = time.clock()
	return now - then

def test2(service, filename):
	service.open(filename,"w+")
	then = time.clock()
	service.write(filename,"HELLO THERE SIR")
	service.write(filename,"I LOVE DOING COS INDEPENDENT WORK")
	service.write(filename,"I LOVE IT SO MUCH")
	service.close(filename)
	service.exit()
	now = time.clock()
	return now - then

tests = [ \
	(test1,    "Simple test"), \
	(test2,    "Multiple writes in single session") \
	]
sizes = ["1kb", "10kb", "100kb", "1mb"]

def testall():
	for n, t in enumerate(tests):
		print
		print "# -------------------------------------- #"
		print "# TEST " + str(n)
		print "# " + str(t[1]) # print test description
		for size in sizes:
			print size
			pfslist = [pfs_service_dropbox(MODE_WRITE), pfs_service_dropbox(MODE_EXIT), pfs_service_dropbox(MODE_CLOSE)]
			for m, pfs in enumerate(pfslist):
				runtime = t[0](pfs, size)
				print "MODE " + str(m) + ": " + str(runtime)

print "MODES:"
print "0: Upload after every write"
print "1: Upload only during exit"
print "2: Upload on close()"

testall()