import sys, os, re

term_index = 'term_index.txt'
term_info = 'term_info.txt'
docids = 'docids.txt'
termids = 'termids.txt '
doc_index = 'doc_index.txt'


def doc(doc_name):
	fp_doc_id = open(docids)
	list = fp_doc_id.readlines()
	doc_id = 0
	for one in list:
		if one.split('\t')[1].strip() == doc_name:
			doc_id = int(one.split('\t')[0].strip())
		
	if doc_id == 0:
		print ('wrong document name')
		return
	
	term_num = 0
	total_term = 0
	fp_doc_index = open(doc_index)
	list = fp_doc_index.readlines()
	fp_doc_index.close()
	
	for one in list:
		if int(one.split('\t')[0].strip()) == doc_id:
			term_num += 1
			#print len(one.split('\t'))
			total_term += len(one.split('\t')) - 2
	print ('Listing for document: ' + doc_name + '\n' + 'DOCID: ' + str(doc_id) + '\n' + 'Distinct terms: ' + str(term_num) + '\n' +'Total terms: ' + str(total_term) + '\n')
	
def term(term_name):
	fp_term_id = open(termids)
	list = fp_term_id.readlines()
	term_id = 0
	for one in list:
		if one.split('\t')[1].strip() == term_name:
			term_id = int(one.split('\t')[0].strip())
	if term_id == 0:
		print ('the term does not exist')
		return
	#print 
	fp_term_index = open(term_info)
	list = fp_term_index.readlines()
	fp_term_index.close()
	for one in list:
		if int(one.split('\t')[0].strip()) == term_id:
			print ('Listing for term: ' + term_name + '\n'
				+ 'TERMID: ' + str(term_id) + '\n'  
				+ 'Number of documents containing term: ' + one.split('\t')[3].strip() + '\n'
				+ 'Term frequency in corpus: '  + one.split('\t')[2].strip() + '\n'
				+ 'Inverted list offset: ' + one.split('\t')[1].strip() + '\n'
			 	)
			break
	

def term_doc(term_name, doc_name):

	fp_doc_id = open(docids)
	list = fp_doc_id.readlines()
	doc_id = 0
	for one in list:
		if one.split('\t')[1].strip() == doc_name:
			doc_id = int(one.split('\t')[0].strip())
	
	fp_term_id = open(termids)
	list = fp_term_id.readlines()
	term_id = 0
	for one in list:
		if one.split('\t')[1].strip() == term_name:
			term_id = int(one.split('\t')[0].strip())
	
	offset = 0
	fp_term_info = open(term_info)
	list = fp_term_info.readlines()
	fp_term_info.close()
	for one in list:
		if int(one.split('\t')[0].strip()) == term_id:
			offset = int(one.split('\t')[1].strip())
			#print (str(term_id), offset)
			break
	print ('Inverted list for term: ' + term_name + '\n'
			+ 'In document: ' + doc_name + '\n'
			+ 'TERMID: ' + str(term_id) + '\n'
			+ 'DOCID: ' + str(doc_id) 
			)
	
	fp_term_index = open(term_index, 'r')
	#fp_term_index.seek(0,0)
	fp_term_index.seek(offset, 0)
	#print offset
	line = fp_term_index.readline().split('\t')
	
	doc_start = int(line[1].split(':')[0])
	frequency = 0
	position = ''
	sum = 0
	if int(doc_start) == doc_id:
		frequency += 1
		position = line[1].split(':')[1]
		sum = int(position)
	#print line
	for i in line[2:]:
		if doc_start + int(i.split(':')[0]) == doc_id:
			frequency += 1
			if position != '':
				sum += int(i.split(':')[1])
				position += ', ' + str(sum)
			else:
				sum += int(i.split(':')[1])
				position += str(sum)
		elif doc_start + int(i.split(':')[0]) < doc_id:
			 doc_start += int(i.split(':')[0])
		else:
			break
	print ('Term frequency in document: ' + str(frequency) + '\n'
			+ 'Positions: ' + position)
	
	
		

if __name__=='__main__':
	#print(sys.argv)
	if len(sys.argv) == 3:
		if sys.argv[1] == '--doc':
			doc(sys.argv[2])
		elif sys.argv[1] == '--term':
			term(sys.argv[2])
	elif len(sys.argv) == 5:
		if sys.argv[1] == '--term' and sys.argv[3] == '--doc':
			term_doc(sys.argv[2], sys.argv[4])
	else:
		print ('wrong command')
	
		
	
