import string
import math
import timeit
import sys
import urllib, re
from collections import defaultdict
from string import punctuation
import xml.etree.ElementTree as ET

#start = timeit.default_timer()

#<topic> is the ID of the query for which the document was ranked.
#0 is part of the format and can be ignored.
#<docid> is the document identifier.
#<rank> is the order in which to present the document to the user. 
#       The document with the highest score will be assigned a rank of 1, the second highest a rank of 2, and so on.
#<score> is the actual score the document obtained for that query.
#<run> is the name of the run. You can use any value here. 
#      It is meant to allow research teams to submit multiple runs for evaluation in competitions such as TREC.

D = 3377  #total number of documents#
D_query = 10

K1 = 1.2
K2 = 100
B = 0.75
V = 179439
N = 0.2

TOPICS = "./topics.xml"
OUTPUT_FILE1 = "TF_output.txt"
OUTPUT_FILE2 = "TF_IDF_output.txt"
OUTPUT_FILE3 = "BM25_output.txt"
OUTPUT_FILE4 = "Lap_output.txt"
OUTPUT_FILE5 = "JM_output.txt"

regular_script = '<\\s*?script[^>]*?>[\\s\\S]*?<\\s*?/\\s*?script\\s*?>'
regular_comment = '<!--(.*?)-->'
#####################################################################################
class PorterStemmer:

	def __init__(self):
		"""The main part of the stemming algorithm starts here.
		b is a buffer holding a word to be stemmed. The letters are in b[k0],
		b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
		readjusted downwards as the stemming progresses. Zero termination is
		not in fact used in the algorithm.

		Note that only lower case sequences are stemmed. Forcing to lower case
		should be done before stem(...) is called.
		"""

		self.b = ""  # buffer for word to be stemmed
		self.k = 0
		self.k0 = 0
		self.j = 0   # j is a general offset into the string

	def cons(self, i):
		"""cons(i) is TRUE <=> b[i] is a consonant."""
		if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
			return 0
		if self.b[i] == 'y':
			if i == self.k0:
				return 1
			else:
				return (not self.cons(i - 1))
		return 1

	def m(self):
		"""m() measures the number of consonant sequences between k0 and j.
		if c is a consonant sequence and v a vowel sequence, and <..>
		indicates arbitrary presence,

		   <c><v>	   gives 0
		   <c>vc<v>	 gives 1
		   <c>vcvc<v>   gives 2
		   <c>vcvcvc<v> gives 3
		   ....
		"""
		n = 0
		i = self.k0
		while 1:
			if i > self.j:
				return n
			if not self.cons(i):
				break
			i = i + 1
		i = i + 1
		while 1:
			while 1:
				if i > self.j:
					return n
				if self.cons(i):
					break
				i = i + 1
			i = i + 1
			n = n + 1
			while 1:
				if i > self.j:
					return n
				if not self.cons(i):
					break
				i = i + 1
			i = i + 1

	def vowelinstem(self):
		"""vowelinstem() is TRUE <=> k0,...j contains a vowel"""
		for i in range(self.k0, self.j + 1):
			if not self.cons(i):
				return 1
		return 0

	def doublec(self, j):
		"""doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
		if j < (self.k0 + 1):
			return 0
		if (self.b[j] != self.b[j-1]):
			return 0
		return self.cons(j)

	def cvc(self, i):
		"""cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
		and also if the second c is not w,x or y. this is used when trying to
		restore an e at the end of a short  e.g.

		   cav(e), lov(e), hop(e), crim(e), but
		   snow, box, tray.
		"""
		if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
			return 0
		ch = self.b[i]
		if ch == 'w' or ch == 'x' or ch == 'y':
			return 0
		return 1

	def ends(self, s):
		"""ends(s) is TRUE <=> k0,...k ends with the string s."""
		length = len(s)
		if s[length - 1] != self.b[self.k]: # tiny speed-up
			return 0
		if length > (self.k - self.k0 + 1):
			return 0
		if self.b[self.k-length+1:self.k+1] != s:
			return 0
		self.j = self.k - length
		return 1

	def setto(self, s):
		"""setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
		length = len(s)
		self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
		self.k = self.j + length

	def r(self, s):
		"""r(s) is used further down."""
		if self.m() > 0:
			self.setto(s)

	def step1ab(self):
		"""step1ab() gets rid of plurals and -ed or -ing. e.g.

		   caresses  ->  caress
		   ponies	->  poni
		   ties	  ->  ti
		   caress	->  caress
		   cats	  ->  cat

		   feed	  ->  feed
		   agreed	->  agree
		   disabled  ->  disable

		   matting   ->  mat
		   mating	->  mate
		   meeting   ->  meet
		   milling   ->  mill
		   messing   ->  mess

		   meetings  ->  meet
		"""
		if self.b[self.k] == 's':
			if self.ends("sses"):
				self.k = self.k - 2
			elif self.ends("ies"):
				self.setto("i")
			elif self.b[self.k - 1] != 's':
				self.k = self.k - 1
		if self.ends("eed"):
			if self.m() > 0:
				self.k = self.k - 1
		elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
			self.k = self.j
			if self.ends("at"):   self.setto("ate")
			elif self.ends("bl"): self.setto("ble")
			elif self.ends("iz"): self.setto("ize")
			elif self.doublec(self.k):
				self.k = self.k - 1
				ch = self.b[self.k]
				if ch == 'l' or ch == 's' or ch == 'z':
					self.k = self.k + 1
			elif (self.m() == 1 and self.cvc(self.k)):
				self.setto("e")

	def step1c(self):
		"""step1c() turns terminal y to i when there is another vowel in the stem."""
		if (self.ends("y") and self.vowelinstem()):
			self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

	def step2(self):
		"""step2() maps double suffices to single ones.
		so -ization ( = -ize plus -ation) maps to -ize etc. note that the
		string before the suffix must give m() > 0.
		"""
		if self.b[self.k - 1] == 'a':
			if self.ends("ational"):   self.r("ate")
			elif self.ends("tional"):  self.r("tion")
		elif self.b[self.k - 1] == 'c':
			if self.ends("enci"):	  self.r("ence")
			elif self.ends("anci"):	self.r("ance")
		elif self.b[self.k - 1] == 'e':
			if self.ends("izer"):	  self.r("ize")
		elif self.b[self.k - 1] == 'l':
			if self.ends("bli"):	   self.r("ble") # --DEPARTURE--
			# To match the published algorithm, replace this phrase with
			#   if self.ends("abli"):	  self.r("able")
			elif self.ends("alli"):	self.r("al")
			elif self.ends("entli"):   self.r("ent")
			elif self.ends("eli"):	 self.r("e")
			elif self.ends("ousli"):   self.r("ous")
		elif self.b[self.k - 1] == 'o':
			if self.ends("ization"):   self.r("ize")
			elif self.ends("ation"):   self.r("ate")
			elif self.ends("ator"):	self.r("ate")
		elif self.b[self.k - 1] == 's':
			if self.ends("alism"):	 self.r("al")
			elif self.ends("iveness"): self.r("ive")
			elif self.ends("fulness"): self.r("ful")
			elif self.ends("ousness"): self.r("ous")
		elif self.b[self.k - 1] == 't':
			if self.ends("aliti"):	 self.r("al")
			elif self.ends("iviti"):   self.r("ive")
			elif self.ends("biliti"):  self.r("ble")
		elif self.b[self.k - 1] == 'g': # --DEPARTURE--
			if self.ends("logi"):	  self.r("log")
		# To match the published algorithm, delete this phrase

	def step3(self):
		"""step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
		if self.b[self.k] == 'e':
			if self.ends("icate"):	 self.r("ic")
			elif self.ends("ative"):   self.r("")
			elif self.ends("alize"):   self.r("al")
		elif self.b[self.k] == 'i':
			if self.ends("iciti"):	 self.r("ic")
		elif self.b[self.k] == 'l':
			if self.ends("ical"):	  self.r("ic")
			elif self.ends("ful"):	 self.r("")
		elif self.b[self.k] == 's':
			if self.ends("ness"):	  self.r("")

	def step4(self):
		"""step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
		if self.b[self.k - 1] == 'a':
			if self.ends("al"): pass
			else: return
		elif self.b[self.k - 1] == 'c':
			if self.ends("ance"): pass
			elif self.ends("ence"): pass
			else: return
		elif self.b[self.k - 1] == 'e':
			if self.ends("er"): pass
			else: return
		elif self.b[self.k - 1] == 'i':
			if self.ends("ic"): pass
			else: return
		elif self.b[self.k - 1] == 'l':
			if self.ends("able"): pass
			elif self.ends("ible"): pass
			else: return
		elif self.b[self.k - 1] == 'n':
			if self.ends("ant"): pass
			elif self.ends("ement"): pass
			elif self.ends("ment"): pass
			elif self.ends("ent"): pass
			else: return
		elif self.b[self.k - 1] == 'o':
			if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
			elif self.ends("ou"): pass
			# takes care of -ous
			else: return
		elif self.b[self.k - 1] == 's':
			if self.ends("ism"): pass
			else: return
		elif self.b[self.k - 1] == 't':
			if self.ends("ate"): pass
			elif self.ends("iti"): pass
			else: return
		elif self.b[self.k - 1] == 'u':
			if self.ends("ous"): pass
			else: return
		elif self.b[self.k - 1] == 'v':
			if self.ends("ive"): pass
			else: return
		elif self.b[self.k - 1] == 'z':
			if self.ends("ize"): pass
			else: return
		else:
			return
		if self.m() > 1:
			self.k = self.j

	def step5(self):
		"""step5() removes a final -e if m() > 1, and changes -ll to -l if
		m() > 1.
		"""
		self.j = self.k
		if self.b[self.k] == 'e':
			a = self.m()
			if a > 1 or (a == 1 and not self.cvc(self.k-1)):
				self.k = self.k - 1
		if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
			self.k = self.k -1

	def stem(self, p, i, j):
		"""In stem(p,i,j), p is a char pointer, and the string to be stemmed
		is from p[i] to p[j] inclusive. Typically i is zero and j is the
		offset to the last character of a string, (p[j+1] == '\0'). The
		stemmer adjusts the characters p[i] ... p[j] and returns the new
		end-point of the string, k. Stemming never increases word length, so
		i <= k <= j. To turn the stemmer into a module, declare 'stem' as
		extern, and delete the remainder of this file.
		"""
		# copy the parameters into statics
		self.b = p
		self.k = j
		self.k0 = i
		if self.k <= self.k0 + 1:
			return self.b # --DEPARTURE--

		# With this line, strings of length 1 or 2 don't go through the
		# stemming process, although no mention is made of this in the
		# published algorithm. Remove the line to match the published
		# algorithm.

		self.step1ab()
		self.step1c()
		self.step2()
		self.step3()
		self.step4()
		self.step5()
		return self.b[self.k0:self.k+1]


######################################################################################



#return the dict in which: 
## key = doc_id
## value = doc name
def docid_mapping():
	docid_map_dict = {}
	with open('docids.txt', 'r') as f:
		for line in f:
			split_line = line.split()
			docid_map_dict[split_line[0]] = split_line[1]
	return docid_map_dict




#return the dict in which: 
## key = term_id
## value = term
def termid_mapping():
	termid_map_dict = {}
	with open('termids.txt', 'r') as f:
		for line in f:
			#print line
			split_line = line.split()
			termid_map_dict[split_line[0]] = split_line[1]
	return termid_map_dict
	#print termid_map_dict

# return the dict in which:
# key = termid
# value = df -- the number of doc which contain the term
def termid_doc_num_mapping():
	termid_doc_num_dict = {}
	with open('term_info.txt', 'r') as f:
		for line in f:
			split_line = line.split()
			termid_doc_num_dict[split_line[0]] = split_line[3]
	return termid_doc_num_dict
	#print termid_doc_num_dict


# return the dict in which:
# key = termid
# value = df -- the number of tern in corpus
def total_term_num_mapping():
	total_term_num_dict = {}
	with open('term_info.txt', 'r') as f:
		for line in f:
			split_line = line.split()
			total_term_num_dict[split_line[0]] = split_line[2]
	return total_term_num_dict
	#print total_term_num_dict




# return the termid using term
def search_termid(value):
	termid_map = termid_mapping()
	query_term_id = 0
	for k, v in termid_map.items():
		if v == value:
			query_term_id = k
	return query_term_id




## Processing the query
def query_processing(txt):
	#print txt
	token_reg = re.compile(r"\w+(?:\.?\w+)*")
	token_txt = re.findall(token_reg, txt)
	#print token_txt
	fp = open('stoplist.txt')
	stoplist = fp.read()
	fp.close()
	#termid_mapping = termid_mapping()
	p = PorterStemmer()
	list_txt = '';
	for elt in token_txt:
		#print elt
		elt = elt.lower()
		if elt not in stoplist:
			#print elt
			value = p.stem(elt, 0, len(elt)-1)
			#print value
			#print value
			id_term = search_termid(value)
			# for k, v in termid_mapping.items():
			# 	if v == value:
			# 		termid = k
			list_txt += str(id_term) + ' '
	#porter_stem(list_txt)
	return list_txt
	#print list_txt


## PURPOSE:
## Returns the dictionary in which:
## key = topic_id
## value = the txt of query after processing
def dict_topic_query():
	#soup = BeautifulSoup('TOPICS')
	topid_query_dict = {}
	with open(TOPICS, 'r') as f:
		tree = ET.parse(f)
		root = tree.getroot()
		for child in root:
			if child.tag == 'topic':
				topic_id = child.get('number')
				query = child.find('query').text
				topid_query_dict[topic_id] = query_processing(query)
		return topid_query_dict
		#print topid_query_dict
			#print child.tag
			


## PURPOSE:
## Returns the averagy query length -- avg(len(q))
def avg_query_len():
	topid_query_dict = dict_topic_query()
	temp_list = []
	temp_dict = {key: len(value) for (key, value) in topid_query_dict.items()}
	len_query = (float(sum([v for v in temp_dict.values()])))
	len_dict = len([temp_list.append(v) for v in temp_dict.values()])
	return len_query/len_dict
	#print len_query/len_dict





## PURPOSE:
## Returns a dictionary in which:
## key = term_id
## value = term frequency
def dict_term_freq():
	query_dict = dict_topic_query()
	term_freq_dict = {}
	for v in query_dict.values():
		for u in v.split():
			term_freq_dict[u] = v.split().count(u)
	return term_freq_dict
	#print term_freq_dict


## PURPOSE:
## Returns the dictionary in which:
## key = term not term_id
## value = length of the query which contains the key
def dict_term_query_len():
	term_query_len_dict = {}
	topid_query_dict = dict_topic_query()
	temp_dict = {key: len(value.split()) for (key, value) in topid_query_dict.items()}
	for k, v in topid_query_dict.items():
		for temp_k, temp_v in temp_dict.items():
			if temp_k == k:
				for u in v.split():
					term_query_len_dict[u] = temp_v
	return term_query_len_dict
	#print term_query_len_dict



## PURPOSE:
## Returns the dictionary in which:
## key = term in a query
## value = the weight of term in that query
def dict_term_in_query_oktf():
	term_freq_dict = dict_term_freq()
	term_query_len_dict = dict_term_query_len()
	avg_len = avg_query_len()
	term_oktf_in_query_dict = {}
	term_oktf_in_query_dict = {k: (float((term_freq_dict[k])/(term_freq_dict[k] + 0.5 + 1.5*(v/avg_len)))) for (k, v) in term_query_len_dict.items()}
	return term_oktf_in_query_dict
	#print term_oktf_in_query_dict


## PURPOSE:
## Returns the dictionary in which:
## key = term in a query
## value = the weight * log(D_query/1)of term in that query
def dict_term_in_query_oktf_log():
	oktf_log_dict = {}
	oktf_dict = dict_term_in_query_oktf()
	for k, v in oktf_dict.items():
		oktf_log_dict[k] = v* math.log(D_query/1)
	return oktf_log_dict#
	#print term_oktf_in_query_dict



## PURPOSE:
## Returns the dictionary in which:
## key = doc_id_term_id
## value = tf(d,i) (the # of term i in document d)
## read doc_index.txt
def docid_termid_mapping():
	docid_termid_map_dict = {}
	with open('doc_index.txt', 'r') as f:
		for line in f:
			split_line = line.split()
			key = split_line[0]+ '_' + split_line[1]
			docid_termid_map_dict[key] = len(split_line) - 2
	return docid_termid_map_dict
	#print docid_termid_map_dict


## Return: 
## key: docid
## value: a array contain termid... in the doc
def dict_docid_terms():
	docid_terms_dict = {}
	with open('doc_index.txt', 'r') as f:
		for line in f:
			split_line = line.split()
			if split_line[0] in docid_terms_dict:
				docid_terms_dict[split_line[0]].append(split_line[1])
			else:
				docid_terms_dict[split_line[0]] = [split_line[1]]
	return docid_terms_dict
	#print docid_terms_dict




## PURPOSE:
## Returns a dictionary in which:
## key = docid
## Returns the document length -- len(d)
def dict_doc_len():
	doc_len_dict = {}
	with open('doc_index.txt', 'r') as f:
		for line in f:
			split_line = line.split()
			if split_line[0] in doc_len_dict:
				doc_len_dict[split_line[0]] += len(split_line) - 2
			else:
				doc_len_dict[split_line[0]] = len(split_line) - 2
			
		# keylist = doc_len_dict()
		# keylist.sort()
		# for key in keylist:
		# 	doc_len_dict[key] = doc_len_dict[key]
		#doc_len_dic = sorted(doc_len_dict.iterkeys())
	return doc_len_dict
	#print doc_len_dict


## Returns the averagy document length -- avg(len(d))
def avg_doc_len():
	doc_len_dict = dict_doc_len()
	len_corpus = (float(sum([v for v in doc_len_dict.values()])))
	len_dict = 0
	for i in doc_len_dict:
		len_dict += 1
	#print len_dict
	return len_corpus/len_dict
	#print len_corpus/D



def dict_doc_di():
	doc_di_dict = {}
	#docid_map_dict = docid_mapping()
	docid_term_freq_dict = docid_termid_mapping()
	len_doc_dict = dict_doc_len()
	avg_len = avg_doc_len()
	docid_terms_dict = dict_docid_terms()
	for k, v in docid_terms_dict.items():
		#print k
		di_dict = defaultdict(lambda: 0)
		for i in v:
			#print i
			termid = k + '_' + i
			#print termid
			#print docid_term_freq_dict[termid]
			#print len_doc_dict[k]
			di_dict[i] = float(docid_term_freq_dict[termid])/(docid_term_freq_dict[termid] + 0.5 + (1.5*(float(len_doc_dict[k])/avg_len)))
			#print di_dict[i]
		doc_di_dict[k] = di_dict
	return doc_di_dict
	#print doc_di_dict


def dict_doc_di_log():
	doc_di_log_dict = {}
	doc_di_dict = dict_doc_di()
	df_dict = termid_doc_num_mapping()
	for k, v in doc_di_dict.items():
		di_log_dict = defaultdict(lambda: 0)
		for k1, v1 in v.items():
			di_log_dict[k1] = v1 * math.log(D/float(df_dict[k1]))
		doc_di_log_dict[k] = di_log_dict
	return doc_di_log_dict
	


def dict_doc_square():
	doc_sq_sum_dict = {}
	doc_di_dict = dict_doc_di()
	for k, v in doc_di_dict.items():
		sq_sum = 0
		for v1 in v.values():
			sq_sum += v1**2
		doc_sq_sum_dict[k] = sq_sum
	return doc_sq_sum_dict 


def dict_doc_square_log():
	doc_sq_sum_dict = {}
	doc_di_log_dict = dict_doc_di_log()
	for k, v in doc_di_log_dict.items():
		sq_sum = 0
		for v1 in v.values():
			sq_sum += v1**2
		doc_sq_sum_dict[k] = sq_sum
	return doc_sq_sum_dict 

	





#############################################################################
## Scoring Function 1: Okapi TF
def TF_module():
	with open(OUTPUT_FILE1, "w") as f:
		query_dict = dict_topic_query()
		query_term_oktf_dict = dict_term_in_query_oktf()
		doci_di_dict = dict_doc_di()
		doc_square_dict = dict_doc_square()
		docid_map_dict = docid_mapping()

		for topid, term_ids in query_dict.items():
			docid_score_dict = defaultdict(lambda: 0)
			#print term_ids
			for k, v in doci_di_dict.items():
				numerator = 0
				#denominator = 0
				q_sq_sum = 0
				doc_sq_sum = doc_square_dict[k]
				for i in term_ids.split():
					#print v[i]
					q_sq_sum += query_term_oktf_dict[i]**2
					if i in v:
						numerator += query_term_oktf_dict[i] * v[i]
					else:
						numerator += 0
				#denominator = math.sqrt(float(q_sq_sum)) * math.sqrt(float(doc_sq_sum))
				docid_score_dict[k] = numerator/(math.sqrt(float(q_sq_sum)) * math.sqrt(float(doc_sq_sum)))
			
			rank = 1 
			for docid, score in sorted(docid_score_dict.items(), key = lambda x: x[1], reverse=True):
				line_of_text = str(topid) + '\t' + '0' + '\t' + docid_map_dict[docid] + '\t' + str(rank) + '\t' + str(score) + '\t' + 'run1' + '\n'
				f.write(line_of_text)
				rank += 1
		f.close



## Scoring Function 2: Okapi TF-IDF
def TF_IDF_module():
	with open(OUTPUT_FILE2, "w") as f:
		query_dict = dict_topic_query()
		query_term_oktf_log_dict = dict_term_in_query_oktf_log()
		doci_di_log_dict = dict_doc_di_log()
		doc_square_log_dict = dict_doc_square_log()
		docid_map_dict = docid_mapping()

		for topid, term_ids in query_dict.items():
			docid_score_dict = defaultdict(lambda: 0)
		
			for k, v in doci_di_log_dict.items():
				q_sq_sum = 0
				numerator = 0
				#denominator = 0
				doc_sq_sum = doc_square_log_dict[k]
				for i in term_ids.split():
					q_sq_sum += query_term_oktf_log_dict[i]**2
					if i in v:
						#print v[i]
						numerator += query_term_oktf_log_dict[i] * v[i]
					else:
						#print 0
						numerator += 0
				docid_score_dict[k] = numerator/(math.sqrt(float(q_sq_sum)) * math.sqrt(float(doc_sq_sum)))
			
			rank = 1 
			for docid, score in sorted(docid_score_dict.items(), key = lambda x: x[1], reverse=True):
				line_of_text = str(topid) + '\t' + '0' + '\t' + docid_map_dict[docid] + '\t' + str(rank) + '\t' + str(score) + '\t' + 'run2' + '\n'
				f.write(line_of_text)
				rank += 1
		f.close




## Scoring Function 3: Okapi BM25
def BM25_module():
	with open(OUTPUT_FILE3, "w") as f:
		query_dict = dict_topic_query()
		tf_di_dict = docid_termid_mapping()
		#doc_dict = dict_docid_terms()
		docid_map_dict = docid_mapping()
		df_dict = termid_doc_num_mapping()
		tf_qi_dict = dict_term_freq()
		len_doc_dict = dict_doc_len()
		avg_len = avg_doc_len()

		for topid, term_ids in query_dict.items():
			docid_score_dict = defaultdict(lambda: 0)
			#docid_score_dict = {}
			

			for key, len_d in len_doc_dict.items():
				K = 1.2 * (0.25 + (0.75 * float(len_d)/avg_len))
				toal_score = 0

				for i in term_ids.split():
					termid = key + '_' + i
					#print termid
					a = math.log((float(D + 0.5)/(float(df_dict[i])+ 0.5)))
					#print a
					#print tf_di_dict[termid_index]
					c = float(101 * tf_qi_dict[i])/(float(100 + tf_qi_dict[i]))
					#print c
					if termid in tf_di_dict:
						#print tf_di_dict[termid]
						b = ((1 + 1.2) * float(tf_di_dict[termid]))/(K + float(tf_di_dict[termid]))
						#toal_score += (math.log((D + 0.5)/(float(df_dict[i])+0.5))) * (((1 + K1) * tf_di_dict[termid])/(K + float(tf_di_dict[termid]))) * (float((1 + K2) * tf_qi_dict[i])/(K2 + float(tf_qi_dict[i])))
					else:
						b = 0
						#print 0
						#toal_score += 0
					#print b
					
					#print c
					toal_score += a*b*c
				#print toal_score
				docid_score_dict[key] = toal_score
				#print docid_score_dict

			rank = 1
			for docid, score in sorted(docid_score_dict.items(), key = lambda x: x[1], reverse = True):
				line_of_text = str(topid) + '\t' + '0' + '\t' + docid_map_dict[docid] + '\t' + str(rank) + '\t' + str(score) + '\t' + 'run3' + '\n'
				f.write(line_of_text)
				rank += 1
		f.close





## Scoring Function 4: Laplace Smoothing
def Laplace_module():
	with open(OUTPUT_FILE4, "w") as f:
		query_dict = dict_topic_query()
		tf_di_dict = docid_termid_mapping()
		#doc_dict = dict_docid_terms()
		docid_map_dict = docid_mapping()
		len_doc_dict = dict_doc_len()
		# for x, i in len_doc_dict.items():
		# 	print i
		

		for topid, term_ids in query_dict.items():
			docid_score_dict = defaultdict(lambda: 0)
			

			for key, len_d in len_doc_dict.items():
				toal_score = 0
				#print len_d
				#print len_d+V
				for i in term_ids.split():
					termid = key + '_' + i
					#print termid
					if termid in tf_di_dict:
						#print (float(tf_di_dict[termid] + 1)/(len_d + V))
						toal_score += math.log((float(tf_di_dict[termid]) + 1)/(len_d + V))
					else:
						toal_score += math.log(float(1)/float(len_d + V))
						#print (float(1)/(len_d + V))
					#print toal_score

					#print c
				docid_score_dict[key] = toal_score

			rank = 1
			for docid, score in sorted(docid_score_dict.items(), key = lambda x: x[1], reverse = True):
				line_of_text = str(topid) + '\t' + '0' + '\t' + docid_map_dict[docid] + '\t' + str(rank) + '\t' + str(score) + '\t' + 'run4' + '\n'
				f.write(line_of_text)
				rank += 1
		f.close






# Scoring Function 5: Jelinek-Mercer Smoothing
def JM_module():
	with open(OUTPUT_FILE5, "w") as f:
		query_dict = dict_topic_query()
		tf_di_dict = docid_termid_mapping()
		#doc_dict = dict_docid_terms()
		docid_map_dict = docid_mapping()
		len_doc_dict = dict_doc_len()
		total_term_num_dict = total_term_num_mapping()
		# for x, i in len_doc_dict.items():
		# 	print i
		sum_len_d = 0
		for  i in len_doc_dict.values():
			sum_len_d += i

		for topid, term_ids in query_dict.items():
			docid_score_dict = defaultdict(lambda: 0)

			for key, len_d in len_doc_dict.items():
				toal_score = 0
				for i in term_ids.split():
					termid = key + '_' + i
					#print termid
					if termid in tf_di_dict:
						#print N*(tf_di_dict[termid]/len_d) + (1-N)*(float total_term_num_dict[i]/sum_len_d)
						toal_score += math.log(N* float(tf_di_dict[termid])/len_d + (1-N)* (float(total_term_num_dict[i])/sum_len_d))
					else:
						toal_score += math.log((1-N) * (float(total_term_num_dict[i])/sum_len_d))
						#print (1-N)*(float total_term_num_dict[i]/sum_len_d)
					#print toal_score

					#print c
				docid_score_dict[key] = toal_score

			rank = 1
			for docid, score in sorted(docid_score_dict.items(), key = lambda x: x[1], reverse = True):
				line_of_text = str(topid) + '\t' + '0' + '\t' + docid_map_dict[docid] + '\t' + str(rank) + '\t' + str(score) + '\t' + 'run5' + '\n'
				f.write(line_of_text)
				rank += 1
		f.close






if __name__=='__main__':
	start = timeit.default_timer()
	#print(sys.argv)
	if len(sys.argv) == 3:
		if sys.argv[2] == 'TF':
			TF_module()
		elif sys.argv[2] == 'TF-IDF':
			TF_IDF_module()
		elif sys.argv[2] == 'BM25':
			BM25_module()
		elif sys.argv[2] == 'Laplace':
			Laplace_module()
		elif sys.argv[2] == 'JM':
			JM_module()
	else:
		print ('wrong command')

	stop = timeit.default_timer()
	print 'running time is:', stop - start


# if __name__ == '__main__':
#  	start = timeit.default_timer()
#  	#TF_module()
# 	#TF_IDF_module()
# 	#BM25_module()
# 	#Laplace_module()
# 	#JM_module()

	
# 	#dict_topic_query()   #7.39
# 	#dict_docid_terms()   1.358
# 	#dict_doc_di()   #7.814
# 	#dict_doc_di_log()  9.517
# 	#dict_doc_square() 7.771
# 	#dict_doc_square_log()  9.5358
# 	#avg_query_len()  1.192
# 	#dict_term_freq()  9,537
# 	#dict_term_query_len()  7.754
# 	#dict_term_in_query_oktf()  22.1732
# 	#dict_term_in_query_oktf_log()  22.16
# 	#docid_termid_mapping()   1.873
# 	#dict_doc_len()   1.434
# 	#avg_doc_len()   #1.437
# 	#docid_mapping()  0.002
# 	#termid_mapping()  0.167
# 	#termid_doc_num_mapping()  0.185
# 	#total_term_num_mapping()   0.173
# 	#search_termid('flag')  0.28
	
# 	stop = timeit.default_timer()
#  	print 'running time is:', stop - start
	

