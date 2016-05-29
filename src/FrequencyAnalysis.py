import re, time, os.path

class Sorter:

	def merge(self, left, right):
	    result = []
	    i ,j = 0, 0
	    while i < len(left) and j < len(right):
	        if left[i][1] <= right[j][1]:
	            result.append(left[i])
	            i += 1
	        else:
	            result.append(right[j])
	            j += 1
	    result += left[i:]
	    result += right[j:]
	    return result
	
	def mergesort(self, _list):
	    if len(_list) < 2:
	        return _list
	    middle = len(_list) / 2
	    left = self.mergesort(_list[:middle])
	    right = self.mergesort(_list[middle:])
	    return self.merge(left, right)

class AnalyzeFrequency:

	def __init__(self, path, _do_sort):
		self.sorter = Sorter()
		self._path = path
		self._do_sort = _do_sort
		self._state = False
		self._time = -1
		self._words = []

	def get_results(self):
		if self._state:
			return self._words
		else:
			return None
	
	def analyze(self):
		start_time = time.time()
		
		try:
			file = open(self._path, 'r')
		except:
			raise IOError

		lines = []
		for line in file:
			lines.append(line)
		file.close()
		
		words = {}
		for x in xrange(0, len(lines)):
			lines[x] = re.sub("[^a-zA-Z\s]", '', lines[x]).lower()
			for word in lines[x].split():
				if word not in words:
					words[word] = 1
				else:
					words[word] += 1
		
		if self._do_sort:
			self._words = self.sorter.mergesort(words.items())
			self._words.reverse()
		else:
			self._words = words.items()
		self._time = time.time() - start_time
		self._state = True

class FrequencyStore:

	def __init__(self, file_name):
		self.sorter = Sorter()
		self.db = {}
		self.file_name = file_name
		self.load_time = -1
		self.save_time = -1
		self.append_time = -1
		self.sort_time = -1
		self.SPLIT_SYMBOL = ":"

	def clear_db(self):
		self.db = {}

	def load_db(self):
		start_time = time.time()

		if os.path.exists(self.file_name):

			try:
				file = open(self.file_name, 'r')
			except:
				raise IOError
	
			self.db = {}
			for line in file:
				word, count = line.strip("\n").split(self.SPLIT_SYMBOL)
				self.db[word] = int(count)
			file.close()

		else:

			self.db = {}

		self.load_time = time.time() - start_time

	def save_db(self):
		start_time = time.time()
		
		try:
			file = open(self.file_name, 'w')
		except:
			raise IOError

		file.truncate(0)
		for x in self.create_sorted_db():
			file.write(x[0] + self.SPLIT_SYMBOL + str(x[1]) + "\n")
		file.close()

		self.save_time = time.time() - start_time

	def create_sorted_db(self):
		_temp_db = []
		if len(self.db) == 0:
			return []
		for key in self.db:
			_temp_db.append([key, self.db[key]])
		_temp_db = self.sort(_temp_db)
		return _temp_db

	def get_db(self):
		return self.db

	def sort(self, _list):
		start_time = time.time()

		_list = self.sorter.mergesort(_list)
		_list.reverse()

		self.sort_time = time.time() - start_time
		return _list

	def append(self, _list):
		start_time = time.time()

		for x in _list:
			if x[0] not in self.db:
				self.db[x[0]] = x[1]
			else:
				self.db[x[0]] += x[1]

		self.append_time = time.time() - start_time