#!/usr/bin/env python

# import requests
import os
from pfs_service_dropbox import pfs_service_dropbox, pfs_file_dropbox

def helper1(service, path):
	f = service.open(path, "r+")
	print path + " contents:"
	print service.read(path)
	service.close(path)

def test1(service):
	print
	print "# TEST 1 ------------------------------------#"
	print "# Testing open with file in root dir."
	print "current_dir: " + service.current_dir
	helper1(service, "chop.py")
	print
	helper1(service, "/glolonial/chop.py")
	print
	helper1(service, "glolonial/chop.py")
	
def test2(service):
	print
	print "# TEST 2 ------------------------------------#"
	print "# Testing chdir (forward and backwards) and finally cd back to HOME"
	service.chdir("HALL MUSIC")
	print "cd HALL MUSIC"
	print "    pwd: " + service.current_dir
	service.chdir(".")
	print "cd ."
	print "    pwd: " + service.current_dir
	service.chdir("..")
	print "cd .."
	print "    pwd: " + service.current_dir
	service.chdir("HALL MUSIC") # still have to implement for cd HALL MUSIC/Eprom
	service.chdir("/")
	print "cd HALL MUSIC"
	print "cd /"
	print "    pwd: " + service.current_dir
	service.chdir("..")
	print "cd .."
	print "    pwd: " + service.current_dir
	try:
		service.chdir("notafolder") # should raise error
	except IOError:
		print "cd notafolder"
		print "    successfully raised IOError"

def test3(service):
	print
	print "# TEST 3 ------------------------------------#"
	print "# Opening, writing, seeking, reading"
	f = service.open("chop.py", "r+")
	print "writing HELLO THERE SIR"
	service.write("chop.py","HELLO THERE SIR")
	service.seek("chop.py", 0, 0)
	print "new contents:"
	print service.read("chop.py")
	service.close("chop.py")

def test4(service):
	print
	print "# TEST 4 ------------------------------------#"
	print "# Checking flags"
	f = service.open("chop.py","r")
	print "trying to write to a read-only file"
	try:
		service.write("chop.py","asdf")
	except IOError:
		print "    successfully raised IOError"
	print "trying to write to a file that wasn't opened"
	try:
		service.write("notafile","blah")
	except IOError:
		print "    successfully raised IOError"

def test5(service):
	print
	print "# TEST 5 ------------------------------------#"
	print "# Making and removing directories"
	service.mkdir("/Reed's Stuff/asdf")
	service.rmdir("/Reed's Stuff/asdf")

	service.mkdir("/dne/dne/dne/dne")

def test6(service):
	print
	print "# TEST 6 ------------------------------------#"
	print "# Remove file"
	service.open("temporary","w+")
	service.close("temporary")
	service.remove("temporary")


service = pfs_service_dropbox()
test1(service)
test2(service)
test3(service)
test4(service)
test5(service)
test6(service)

service.logout()
