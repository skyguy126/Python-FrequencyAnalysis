import time, sys, random, os, math
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from multiprocessing import Queue, Process
from FrequencyAnalysis import FrequencyStore, AnalyzeFrequency

class Analyze:

    def __init__(self, base_filename, queue, NUM_OF_SAMPLES, NUM_TOP_WORDS, filelist, ALPHA_VALUE):
        self.queue = queue
        self.filelist = filelist
        self.base_filename = base_filename
        self.database = FrequencyStore(self.base_filename + "_database.txt")
        self.NUM_TOP_WORDS = NUM_TOP_WORDS
        self.NUM_OF_SAMPLES = NUM_OF_SAMPLES
        self.ALPHA_VALUE = ALPHA_VALUE

    def calculate_and_queue(self):
        self.queue.put(self.calculate_confidence_interval())
    
    def calculate_confidence_interval(self):
        books_to_analyze = random.sample(xrange(0 ,len(self.filelist)-1), self.NUM_OF_SAMPLES)
        counter = 1
        for x in books_to_analyze:
            a = AnalyzeFrequency("books/" + self.filelist[x], False)
            a.analyze()
            self.database.append(a.get_results())
            counter += 1
        if self.NUM_TOP_WORDS == -1:
            working_set = self.database.create_sorted_db()
        else:
            working_set = self.database.create_sorted_db()[:self.NUM_TOP_WORDS]
        self.database.clear_db()
        xvals = [i for i in range(0, len(working_set))]
        yvals = []
        for i in xrange(0, len(working_set)):
            yvals.append(working_set[i][1])
    
        xvals = [i for i in range(1, len(working_set)+1)]
        for i in xrange(0, len(working_set)):
            xvals[i] = math.log(xvals[i])
            yvals[i] = math.log(yvals[i])
    
        X = sm.add_constant(xvals)
        model = sm.OLS(yvals, X)
        results = model.fit()
        
        conf_interval = results.conf_int(self.ALPHA_VALUE)[1]
        slope = results.params[1]
        intercept = results.params[0]
        std_err = results.bse[0]

        return conf_interval
    
    def generate_base_graph(self, file_name, xvals, yvals):
        plt.plot(xvals, yvals, 'ro')
        plt.axis([0, xvals[len(xvals)-1]*1.25, 0, yvals[0]*1.25])
        plt.savefig(self.base_filename + "_base_graph.png")
    
    def generate_regression_graph(self, file_name, xvals, yvals, slope, intercept):
        point_a = [xvals[0], (xvals[0] * slope) + intercept]
        point_b = [xvals[len(xvals)-1], (xvals[len(xvals)-1] * slope) + intercept]
        plt.plot(xvals, yvals, 'ro')
        plt.plot([point_a[0], point_b[0]], [point_a[1], point_b[1]], '--')
        plt.axis([0, xvals[len(xvals)-1]*1.25, 0, yvals[0]*1.25])
        plt.savefig(self.base_filename + "_regression_graph.png")

def process_all(queue, confints, process_name, NUM_OF_SAMPLES, NUM_TOP_WORDS, filelist, ALPHA_VALUE):
    analyze = Analyze("worker" + process_name, confints, NUM_OF_SAMPLES, NUM_TOP_WORDS, filelist, ALPHA_VALUE)
    while True:
        if queue.empty():
            return
        queue.get()
        analyze.calculate_and_queue()

def main():
    print "\nLoading file list..."
    filelist = os.listdir("books")
    print "Found %d files..." % len(filelist)

    print "Building queues..."
    start_time = time.time()

    confints = Queue()
    items = Queue()
    for i in xrange(0, NUM_INTERVALS):
        items.put(i)

    print "Starting %d processes..." % NUM_PROCESSES

    processes = []
    for i in xrange(0, NUM_PROCESSES):
        processes.append(Process(target=process_all, args=(items, confints, str(i), NUM_OF_SAMPLES, NUM_TOP_WORDS, filelist, ALPHA_VALUE,)))
        processes[i].daemon = True
        processes[i].start()
        print "Worker %d started..." % i

    print "Processes started..."

    file = open("conf.txt", 'w')
    file.truncate(0)
    for i in xrange(1, NUM_INTERVALS+1):
        file.write(str(i) + ". " + str(confints.get()) + "\n") 
        print "{}% complete...\r".format((float(i)/(NUM_INTERVALS) * 100.0)),
        sys.stdout.flush()
    file.close()

    print "\nTOTAL TIME: " + str(time.time() - start_time)

    sys.exit(0)
        
if __name__=="__main__":
    NUM_OF_SAMPLES = 1500

    #set to -1 to use all words (not recommended)
    NUM_TOP_WORDS = -1
    
    NUM_INTERVALS = 100
    NUM_PROCESSES = 8
    ALPHA_VALUE = 0.05

    assert NUM_PROCESSES > 0
    assert NUM_INTERVALS > 0
    assert NUM_TOP_WORDS > 0 or NUM_TOP_WORDS == -1
    assert NUM_OF_SAMPLES > 0
    assert ALPHA_VALUE > 0 and ALPHA_VALUE < 1
    main()