#!/usr/bin/env python

# import requests
import time
from pfs_service_dropbox import *
import matplotlib.pyplot as plt
import numpy as np

# GLOBAL VARS --------------------------------------- #
ITERATIONS = 2
NUM_MODES = 2
NUM_SIZES = 2

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

class size:
	def __init__(self, size, num):
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

def test1(service, filename):
	service.open(filename,"r+")
	then = time.clock()
	service.write(filename,"HELLO THERE SIR")
	service.write(filename,"I LOVE DOING COS INDEPENDENT WORK")
	service.write(filename,"I LOVE IT SO MUCH")
	service.close(filename)
	service.exit()
	now = time.clock()
	return now - then

def test2(service, filename):
	service.open(filename,"w+")
	then = time.clock()
	content = service.read(filename)
	for i in range(len(content)):
		service.write(filename, "b")
	service.close(filename)
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
			print size.size
			for pfs in pfslist:
				for i in range(ITERATIONS):
					runtime = test.testfunc(pfs, filename=size.size)
					test.add_runtime(pfs.mode, size, runtime)
					print "MODE " + str(pfs.mode) + ": " + str(runtime)

def plotall(pfslist, tests, sizes):
	width = 0.2
	ind = np.arange(NUM_SIZES)

	for test in tests:
		ax = plt.subplot(1,1,1)
		ax.set_title('Elapsed Time for Test ' + str(test.num) + ' for Various Modes')
		ax.set_ylabel('Time')
		ax.set_xlabel('File Sizes')
		ax.set_xticks(ind+width)
		ax.set_xticklabels([size.size for size in sizes])

		for i in range(NUM_MODES):
			print test.get_size_avgs(i)
			print ind+(test.num*width)
			ax.bar(ind+(test.num*width), test.get_size_avgs(i), width, color='y')
		plt.show()

# MAIN() --------------------------------------- #
if __name__ == "__main__":
	
	# OBJECTS --------------------------------------- #
	tests = [ \
		test(testfunc=test0, num=0,    desc="Simple test"),                           \
		# test(testfunc=test1, num=1,    desc="Multiple writes in single session"),     \
		# test(testfunc=test2, num=2,    desc="Lots of really small writes"),           \
		]
	pfslist = [ \
		pfs_wrapper(MODE_WRITE,   "0: Upload after every write"),     \
		pfs_wrapper(MODE_EXIT,    "1: Upload only during exit"),      \
		# pfs_wrapper(MODE_CLOSE,   "2: Upload on close()"),            \
		]
	sizes = [ \
		size("1kb",    0),    \
		size("10kb",   1),    \
		# size("100kb",  2),    \
		# size("1mb",    3),    \
		]


	print "MODES:"
	for pfs in pfslist:
		print pfs.desc

	testall(pfslist, tests, sizes)
	plotall(pfslist, tests, sizes)
