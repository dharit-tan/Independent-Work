#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import sys
import time

NUM_MODES = 3
NUM_SIZES = 4
sizes = ['1kb','10kb','100kb','1mb']
vendors = ['(Dropbox)','(Google Drive)','(Box)']
vendoracrs = ['d','g','b']

def getem():
	vstring = sys.argv[1].strip('\n')
	if vstring == 'dropbox':
		vendor = 0
	elif vstring == 'googledrive':
		vendor = 1
	elif vstring == 'box':
		vendor = 2
	else:
		print vstring
		print "wtf man"
		return

	for testnum in range(8):
		stats = []
		for i in range(NUM_MODES):
			stats.append([])
			for j in range(NUM_SIZES):
				stats[i].append([])

	

		f = open(vendoracrs[vendor]+"test"+str(testnum)+".txt")
		print vendoracrs[vendor]+"test"+str(testnum)
		for l in f.readlines():
			if l[0] == '#':
				continue
			if l == '\n':
				continue
			# print l
			if l.strip('\n') in sizes:
				s = l.strip('\n')
				sizeindex = sizes.index(s)
				continue
			l = l.split()
			mode = int(l[1][0])
			runtime = float(l[2])
			stats[mode][sizeindex].append(runtime)
		for mode in range(NUM_MODES):
			print "mode" + str(mode)
			for s in range(NUM_SIZES):
				print sizes[s]
				print stats[mode][s]

		width = 0.4 / float(NUM_MODES)
		ind = np.arange(NUM_SIZES)

		ax = plt.subplot(1,1,1)
		ax.set_title('Elapsed Time for Test ' + str(testnum) + ' for Various Modes '+vendors[vendor])
		ax.set_ylabel('Time')
		ax.set_xlabel('File Sizes')
		ax.set_xticks(ind+0.2)
		ax.set_xticklabels([size for size in sizes])

		# hopefully we don't run out of colors...
		colors = ['r','y','g','b','m','k','c']
		rects = []
		print "yo here we are"
		for mode in range(NUM_MODES):
			print "mode: " + str(mode)
			print [np.mean(stats[mode][j]) for j in range(NUM_SIZES)]
		for mode in range(NUM_MODES):
			r = ax.bar(ind+(mode*width), [np.mean(stats[mode][j]) for j in range(NUM_SIZES)], width, color=colors[mode], yerr=[np.std(stats[mode][j]) for j in range(NUM_SIZES)])
			rects.append(r)

		# Shink current axis by 20%
		box = ax.get_position()
		ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])

		# Put a legend to the right of the current axis
		ax.legend(rects, ['mode ' + str(mode) for mode in range(3)], loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True)
		plt.show()

getem()