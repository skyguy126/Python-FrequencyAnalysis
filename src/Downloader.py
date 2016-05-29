import urllib2, urllib, zipfile, shutil, os, os.path, sys, random, threading
from BeautifulSoup import BeautifulSoup
from ConfigParser import ConfigParser
from Queue import PriorityQueue

def harvest(input_url):
	books = []
	page_url = input_url
	assert page_url != ""
	print "Analyzing url..."
	html_page = urllib2.urlopen(page_url)
	soup = BeautifulSoup(html_page)
	for link in soup.findAll('a'):
		books.append(str(link.get('href')))
	print "Starting download..."
	offset = books[len(books)-1]
	offset = offset[offset.index("=")+1:offset.index("&")]
	books = books[:len(books)-2]
	for url in books:
		complete = float(books.index(url))/len(books) * 100.0
		print("%.2f percent complete...\r" % complete),
		try:
			if url.index("-h") or url.index("-m"):
				continue
		except:
			pass
		file_name = url[url.rfind('/')+1:]
		try:
			file_name.index(".zip")
		except:
			continue
		urllib.urlretrieve (url, "temp/" + file_name)
		try:
			compressed = zipfile.ZipFile("temp/" + file_name)
			compressed.extractall("temp/")
			compressed.close()
		except:
			continue
		os.remove("temp/" + file_name)
		folder_name = file_name[:file_name.index(".zip")]
		try:
			shutil.copy2("temp/" + folder_name + "/" + folder_name + ".txt", "temp/")
			shutil.rmtree("temp/" + folder_name)
		except:
			pass
		file_name = folder_name + ".txt"
		if os.path.exists("temp/" + file_name):
			pass
		else:
			continue	
		try:
			file = open("temp/" + file_name, 'r+')
			contents = file.read()
			bindex = contents.index("*** START OF THIS PROJECT GUTENBERG EBOOK")+42
			eindex = contents.index("*** END OF THIS PROJECT GUTENBERG EBOOK")
			contents = contents[bindex : eindex]
			file.seek(0)
			file.truncate()
			file.write(contents.strip())
		except:
			pass
	print
	print "Cleaning up..."
	dirs = os.walk("temp")
	dir_list = next(dirs)
	for x in dir_list[1]:
		shutil.rmtree("temp/" + x)
	for x in dir_list[2]:
		try:
			if x.index(".txt"):
				continue
		except:
			os.remove("temp/" + x)
	print "Done!"
	return offset

def read_config(config):
	if os.path.exists("Downloader_Config.ini"):
		try:
			with open("Downloader_Config.ini", "r") as c:
				parser = ConfigParser()
				parser.readfp(c)
				config["offset"] = parser.get("default", "offset")
		except:
			raise Exception("Could not read or create config file!")
	else:
		try:
			with open("Downloader_Config.ini", "w") as c:
				c.write("[default]\n")
				c.write("offset : 0")
			config['offset'] = "0"
		except:
			raise Exception("Could not read or create config file!")

def save_config(config):
	try:
		with open("Downloader_Config.ini", "w") as c:
			c.write("[default]\n")
			c.write("offset : " + config['offset'])
	except:
		raise Exception("Could not save config file!")

def download(queue, config):
	queue.put((1, "default"))
	for i in xrange(0, config['passes']):
		state = queue.get()[1]
		if state == None:
			queue.task_done()
			return
		queue.task_done()
		print "Pass #" + str(i) + " Offset: " + config['offset']
		config['offset'] = harvest(url_start + config['offset'] + url_end)
		queue.put((1, "default"))
	print "\n\nALL PASSES FINISHED!"
	print "Press enter to exit..."

if __name__=="__main__":
	url_start = "http://www.gutenberg.org/robot/harvest?offset="
	url_end = "&filetypes[]=txt&langs[]=en"
	config = {'offset' : "default", 'passes' : -1}
	read_config(config)

	queue = PriorityQueue()
	config['passes'] = int(raw_input("Number of passes: "))
	t = threading.Thread(target=download, args=(queue, config,))
	t.daemon = True
	t.start()
	raw_input("Press enter at anytime to quit...")
	queue.put((0, None))
	t.join()
	save_config(config)
	sys.exit(0)