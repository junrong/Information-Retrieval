import sys, os, re

out_1 = 'term_index.txt'
out_2 = 'term_info.txt'

in_file = 'doc_index.txt'

dict={}
'''
def binary_search(l,key):
	#if not hi:
	#	hi = len(l)
	#if hi < 1:
	#	return -1
	for i in range(0, len(l)-1):
		if int(l[i][0]) == key:
			return i
	return -1
'''
	
def sub_term(line_split, termlist):
	for pos in line_split[2:]:
		termlist.append(line_split[0]+':'+pos)

def delta_encode(list):
	
	#print (list)
	resultlist=[]
	for line in list:
		newlist = line[0:2]
		#print newlist
		pos = int(line[1].split(':')[1])
		docid = int(line[1].split(':')[0])
		for i in line[2:]:
			num = i.split(':')
			if int(num[0]) == docid:
				temp_pos = int(num[1]) - pos
				pos =int(num[1])
				newlist.append('0'+':'+str(temp_pos))
			else:
				temp_docid = int(num[0]) - docid
				docid = int(num[0])
				pos = int(num[1])
				newlist.append(str(temp_docid)+':'+num[1])
		#print newlist
		resultlist.append(newlist)
	#print resultlist
	fp1 = open(out_1, 'w')
	fp2 = open(out_2, 'w')
	for line in resultlist:
		content = str(line[0])
		for one in line[1:]:
			content += '\t' + str(one)
		
		count = 0
		for one in line[1:]:
			if int(one.split(':')[0]) > 0:
				count += 1
		#print fp1.tell()
		fp2.writelines(str(line[0]) + '\t' + str(fp1.tell()) + '\t' + str(len(line) - 1) + '\t' + str(count) + '\n')
		fp1.writelines(content + '\n')
	fp1.close()
	fp2.close()

		
def reverse(linelist):
	
	map_1 = []
	dict = {}
	j = 0
	for line in linelist:
		li = line.split()
		termid = li[1]
		
		
		#k = binary_search(map_1, int(termid))
		#print k
		if int(termid) in dict:
			sub_term(li, map_1[dict.get(int(termid))])
		else:
			newlist = [termid]
			sub_term(li, newlist) 
			map_1.append(newlist)
			dict[int(termid)] = j
			j += 1
	
	map_1 = sorted(map_1)
	#print map_1		
	delta_encode(map_1)
	#deal_term_info(term_index)
	

if __name__=='__main__':
	fp = open(in_file)
	linelist = fp.readlines()
	fp.close()
	reverse(linelist)
