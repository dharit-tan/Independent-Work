#!/usr/bin/env python

# import requests
import os
from parrot_fs_dropbox import pfs_service_dropbox, pfs_file_dropbox

def test1(service):
	print
	print "# TEST 1 ------------------------------------#"
	print "# Testing open with file in root dir. Should see contents of chop.py"
	f = service.open("chop.py", "r+")
	for i in f.readlines():
		print i
	service.close("chop.py")
	
def test2(service):
	print
	print "# TEST 2 ------------------------------------#"
	print "# Testing chdir (forward and backwards) and finally cd back to HOME"
	service.chdir("HALL MUSIC")
	print os.getcwd()
	service.chdir(".")
	print os.getcwd()
	service.chdir("..")
	print os.getcwd()
	service.chdir("HALL MUSIC") # still have to implement for cd HALL MUSIC/Eprom
	service.chdir("/")
	print os.getcwd()
	service.chdir("..")
	print os.getcwd()
	service.chdir("notafolder") # should raise error

service = pfs_service_dropbox()
# test1(service)
test2(service)