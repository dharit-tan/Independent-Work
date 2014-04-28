#!/usr/bin/env python

# import requests
import time
from pfs_service_dropbox import *
import matplotlib.pyplot as plt
import numpy as np
import os
import urllib3.exceptions

# GLOBAL VARS --------------------------------------- #
ITERATIONS = 50
NUM_MODES = 3
NUM_SIZES = 4

# CLASSES --------------------------------------- #
class test:
	def __init__(self, testfunc, num, desc):
		self.testfunc = testfunc
		self.num = num
		self.desc = desc
		self.stats = []
		for i in range(NUM_MODES):
			self.stats.append([])
			for j in range(NUM_SIZES):
				self.stats[i].append([])

	def add_runtime(self, mode, size, runtime):
		self.stats[mode][size.num].append(runtime)

	def get_size_avgs(self, mode):
		# ret = []
		# for i in range(NUM_SIZES):
		# 	ret.append(np.mean(self.stats[mode][i]))
		# return ret
		return [np.mean(self.stats[mode][i]) for i in range(NUM_SIZES)]

	def get_size_std(self, mode):
		return [np.std(self.stats[mode][i]) for i in range(NUM_SIZES)]

class size:
	def __init__(self, sizestr, size, num):
		self.sizestr = sizestr
		self.size = size
		self.num = num

class pfs_wrapper(pfs_service_dropbox):
	def __init__(self, mode, desc):
		pfs_service_dropbox.__init__(self, mode)
		self.desc = desc

# TESTS --------------------------------------- #
def test0(service, filename):
	service.open(filename,"r+")
	then = time.clock()
	service.write(filename,"HELLO THERE SIR")
	service.close(filename)
	service.exit()
	now = time.clock()
	return now - then

# had to put in seeks before every write because of really weird bug where first write would work and be
# at beginning of file, but subsequent writes would all be appended to end of file. wtf.
def test1(service, filename):
	service.open(filename,"r+")
	then = time.clock()
	service.write(filename,"HELLO THERE SIR")
	service.write(filename,"I LOVE DOING COS INDEPENDENT WORK")
	service.write(filename,"I LOVE IT SO MUCH")
	service.write(filename,"123456778890")
	service.write(filename,"123456778890")
	service.write(filename,"123456778890")
	service.write(filename,"123456778890")
	service.close(filename)
	service.exit()
	now = time.clock()
	return now - then

def test2(service, filename):
	service.open(filename,"r+")
	then = time.clock()
	service.seek(filename,0)
	for i in range(20):
		service.write(filename, "b")
	service.close(filename)
	service.exit()
	now = time.clock()
	return now - then

def test3(service, filename):
	then = time.clock()

	service.open(filename, "r+")
	content = service.read(filename)
	service.seek(filename, 0)
	service.write(filename, "asdf")
	service.close(filename)

	service.open(filename, "w+")
	service.write(filename, ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(content))))
	service.seek(filename, 0)
	service.read(filename)
	service.close(filename)

	# service.open(filename, "a+")
	# print "after open: " + str(service.fd_table['/'+filename].fp.tell())
	# service.seek(filename, 0)
	# print "after seek: " + str(service.fd_table['/'+filename].fp.tell())
	# service.read(filename)
	# print "after read: " + str(service.fd_table['/'+filename].fp.tell())
	# service.seek(filename, 0)
	# print "after seek: " + str(service.fd_table['/'+filename].fp.tell())
	# r = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(content)))
	# print r
	# print "len(r): " +str(len(r))
	# service.write(filename, r)
	# print "len content: " + str(len(content))
	# print "after write: " + str(service.fd_table['/'+filename].fp.tell())
	# service.close(filename)

	service.exit()
	now = time.clock()
	return now - then

def test4(service, filename):
	then = time.clock()
	for i in range(10):
		service.open(filename,"r+")
		service.write(filename, "hello")
		service.close(filename)
	service.exit()
	now = time.clock()
	return now - then

def test5(service, filename):
	service.open(filename,"r+")
	service.open(filename+'0',"r+")
	service.open(filename+'1',"r+")
	then = time.clock()

	# old = os.getcwd()
	# os.chdir(DROPBOX_DIR)
	# a = os.stat(service.fd_table['/'+filename].local_name).st_size
	# b = os.stat(service.fd_table['/'+filename+'0'].local_name).st_size
	# c = os.stat(service.fd_table['/'+filename+'1'].local_name).st_size
	# os.chdir(old)

	content = service.read(filename)
	service.seek(filename, 0)
	service.write(filename, ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(content))))
	content = service.read(filename+'0')
	service.seek(filename+'0', 0)
	service.write(filename+'0', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(content))))
	content = service.read(filename+'1')
	service.seek(filename+'1', 0)
	service.write(filename+'1', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(content))))

	# old = os.getcwd()
	# os.chdir(DROPBOX_DIR)
	# d = os.stat(service.fd_table['/'+filename].local_name).st_size
	# e = os.stat(service.fd_table['/'+filename+'0'].local_name).st_size
	# f = os.stat(service.fd_table['/'+filename+'1'].local_name).st_size
	# os.chdir(old)

	# if (a != d):
	# 	print filename + " size got changed"
	# if (b != e):
	# 	print filename+'0'+" size got changed"
	# if (c != f):
	# 	print filename+'1' + " size got changed"

	service.close(filename)
	service.close(filename+'0')
	service.close(filename+'1')
	service.exit()
	now = time.clock()
	return now - then

def test6(service, filename):
	service.open(filename,"r+")
	service.open(filename+'0',"r+")
	service.open(filename+'1',"r+")

	then = time.clock()
	content = service.read(filename)
	service.seek(filename, 0)
	service.write(filename, ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(content))))
	service.close(filename)
	content = service.read(filename+'0')
	service.seek(filename+'0', 0)
	service.write(filename+'0', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(content))))
	service.close(filename+'0')
	content = service.read(filename+'1')
	service.seek(filename+'1', 0)
	service.write(filename+'1', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len(content))))
	service.close(filename+'1')
	service.exit()
	now = time.clock()
	return now - then

def test7(service, filename):
	then = time.clock()
	service.open(filename,"r+")
	service.open(filename+'0',"r+")
	service.open(filename+'1',"r+")
	
	service.read(filename)
	service.seek(filename, 0)
	service.write(filename+'0', "HELLO THERE")
	service.seek(filename+'0',0)
	service.write(filename+'0', "BYE NOW")
	service.seek(filename+'0',10)
	service.write(filename, "HELLO THERE")
	service.close(filename+'1')
	service.open(filename+'1',"r+")

	service.read(filename+'1')
	service.seek(filename+'1',0)

	service.read(filename+'0')
	service.close(filename+'0')
	service.open(filename+'0')
	service.seek(filename+'0',0)
	service.read(filename+'0')
	service.seek(filename+'0',0)
	service.read(filename+'0')
	service.seek(filename,0)
	service.write(filename, "HELLO THERE")
	service.write(filename+'1', "HELLO THERE")

	service.close(filename)
	service.close(filename+'0')
	service.close(filename+'1')
	service.exit()
	now = time.clock()
	return now - then


# FUNCS ------------------------------------------ #
def testall(pfslist, tests, sizes):
	for test in tests:
		print
		print "# -------------------------------------- #"
		print "# TEST " + str(test.num)
		print "# " + str(test.desc)
		for size in sizes:
			print size.sizestr
			for pfs in pfslist:
				for i in range(ITERATIONS):
					try:
						runtime = test.testfunc(pfs, filename=size.sizestr)
						test.add_runtime(pfs.mode, size, runtime)
						print "MODE " + str(pfs.mode) + ": " + str(runtime)
					except (dropbox.rest.ErrorResponse, urllib3.exceptions.ReadTimeoutError, ssl.SSLError):
						pass

def plotall(pfslist, tests, sizes):
	width = 0.4 / float(NUM_MODES)
	ind = np.arange(NUM_SIZES)

	for test in tests:
		ax = plt.subplot(1,1,1)
		ax.set_title('Elapsed Time for Test ' + str(test.num) + ' for Various Modes (Dropbox)')
		ax.set_ylabel('Time')
		ax.set_xlabel('File Sizes')
		ax.set_xticks(ind+0.2)
		ax.set_xticklabels([size.sizestr for size in sizes])

		# hopefully we don't run out of colors...
		colors = ['r','y','g','b','m','k','c']
		rects = []
		for i in range(NUM_MODES):
			r = ax.bar(ind+(i*width), test.get_size_avgs(i), width, color=colors[i], yerr=test.get_size_std(i))
			rects.append(r)

		# Shink current axis by 20%
		box = ax.get_position()
		ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])

		# Put a legend to the right of the current axis
		ax.legend(rects, ['mode ' + str(pfs.mode) for pfs in pfslist], loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True)
		plt.show()

# MAIN() --------------------------------------- #
if __name__ == "__main__":
	
	# OBJECTS --------------------------------------- #
	tests = [ \
		# test(testfunc=test0, num=0,    desc="Simple test"),                                                                   \
		# test(testfunc=test1, num=1,    desc="Multiple writes in single session"),                                             \
		# test(testfunc=test2, num=2,    desc="Lots of really small writes"),                                                   \
		# test(testfunc=test3, num=3,    desc="Open the file in r+ and w+ modes"),                                            \
		# test(testfunc=test4, num=4,    desc="Many alternating write()'s' and close()'s"),                                     \
		# test(testfunc=test5, num=5,    desc="Three files open concurrently, written to, then closed together at the end"),    \
		# test(testfunc=test6, num=6,    desc="Three files open concurrently, written to, then closed right afterwards"),       \
		test(testfunc=test7, num=7,    desc="Three files open concurrently, random operations"),       \
		]
	pfslist = [ \
		pfs_wrapper(MODE_WRITE,   "0: Upload after every write"),     \
		pfs_wrapper(MODE_CLOSE,   "1: Upload on close()"),            \
		pfs_wrapper(MODE_EXIT,    "2: Upload only during exit"),      \
		]
	sizes = [ \
		size("1kb",    1024,       0),    \
		size("10kb",   10240,      1),    \
		size("100kb",  102400,     2),    \
		size("1mb",    1048576,    3),    \
		]


	print "MODES:"
	for pfs in pfslist:
		print pfs.desc

	testall(pfslist, tests, sizes)
	plotall(pfslist, tests, sizes)
