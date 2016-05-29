import time, sys, random, threading, os, math
import matplotlib.pyplot as plt
import numpy as np
from Queue import Queue
import statsmodels.api as sm
from FrequencyAnalysis import FrequencyStore, AnalyzeFrequency

database = FrequencyStore("results.txt")
append_queue = Queue()

def add_to_append_queue(_list):
	append_queue.put(_list)

def process_append_queue():
	while True:
		item = append_queue.get()
		database.append(item)
		append_queue.task_done()

def calculate_population_slope():
	xvals = []
	yvals = []
	for i in xrange(1, 1000):
		xvals.append(math.log(i))
		yvals.append(math.log(1.0/float(i)))

	X = sm.add_constant(xvals)
	model = sm.OLS(yvals, X)
	results = model.fit()
	print str(results.params[1])

def calculate_confidence():
	database.load_db()
	print("Database loaded in %.4f seconds" % database.load_time)
	t = threading.Thread(target=process_append_queue)
	t.daemon = True
	t.start()

	database.clear_db()
	book_list = os.listdir("books")
	books_to_analyze = random.sample(xrange(0 ,len(book_list)-1), NUM_OF_SAMPLES)
	counter = 1
	for x in books_to_analyze:
		a = AnalyzeFrequency("books/" + book_list[x], False)
		a.analyze()
		add_to_append_queue(a.get_results())
		print str(counter) + ". Analyzed " + book_list[x] + " in %.4f seconds" % a._time
		counter += 1
	print "Waiting for appending to finish..."
	append_queue.join()
	database.save_db()
	print("Database saved in %.4f seconds" % database.save_time)

	working_set = database.create_sorted_db()[:NUM_TOP_WORDS]
	xvals = [i for i in range(0, NUM_TOP_WORDS)]
	yvals = []
	for i in xrange(0, len(working_set)):
		yvals.append(working_set[i][1])

	#plt.plot(xvals, yvals, 'ro')
	#plt.axis([0, xvals[len(xvals)-1]*1.25, 0, yvals[0]*1.25])
	#plt.savefig("graph_base.png")

	#regression analysis

	xvals = [i for i in range(1, NUM_TOP_WORDS+1)]
	for i in xrange(0, NUM_TOP_WORDS):
		xvals[i] = math.log(xvals[i])
		yvals[i] = math.log(yvals[i])

	X = sm.add_constant(xvals)
	model = sm.OLS(yvals, X)
	results = model.fit()
	
	conf_interval = results.conf_int()[1]
	slope = results.params[1]
	intercept = results.params[0]
	std_err = results.bse[0]

	point_a = [xvals[0], (xvals[0] * slope) + intercept]
	point_b = [xvals[len(xvals)-1], (xvals[len(xvals)-1] * slope) + intercept]

	#resid_vals = [i for i in results.resid]

	#probplot = sm.ProbPlot(results.resid)
	#probplot.probplot()
	#plt.show()

	print "Slope: " + str(slope)
	print "Intercept: " + str(intercept)

	plt.plot(xvals, yvals, 'ro')
	plt.plot([point_a[0], point_b[0]], [point_a[1], point_b[1]], '--')
	plt.axis([0, xvals[len(xvals)-1]*1.25, 0, yvals[0]*1.25])
	plt.savefig("graph_linreg.png")

	print "\n" + str(conf_interval)
	return conf_interval

def main():
	calculate_confidence()
	#start_time = time.time()
	#file = open("conf.txt", 'w')
	#for i in xrange(1, 101):
	#	print "\n\n-----TRIAL: " + str(i) + " -----"
	#	file.write(str(i) + ". " + str(calculate_confidence()) + "\n")
	#file.close()
	#print "\n\n\nTOTAL TIME: " + str(time.time()-start_time) + " SECONDS"


if __name__=="__main__":
	NUM_OF_SAMPLES = 300
	NUM_TOP_WORDS = 1000
	assert NUM_TOP_WORDS > 0
	assert NUM_OF_SAMPLES > 0
	main()