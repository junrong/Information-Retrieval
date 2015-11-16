#!/usr/bin/python
# -*- coding: utf-8 -*- 

from collections import Counter


# count the total number of words 
def counterTotalWords(words):
	total_quantity = 0
	for w in words:
		total_quantity += 1
	return total_quantity


# count the the total number of unique words
def countUniWords(words):
	uni_quantity = 0
	visited = []
	for w in words:
		if w not in visited:
			uni_quantity += 1
			visited.append(w)
	return uni_quantity


# find the top n most frequent words
def topWords(words, n):
	rank = 0
	ctw = Counter(words)
	top25Words = ctw.most_common(n)
	for w in top25Words:
		rank += 1
		print w[0], '\t', w[1], '\t\t', rank, '\t', probability(w[1], counterTotalWords(words)), '\t\t', rank * probability(w[1], counterTotalWords(words))

# find the most frequent 25 additional words that start 
# with the letter f
def topWord_f(words, n, visited):
	f_list = []
	for w in words:
		if w.startswith('f') and w not in visited:
			f_list.append(w)
	top25Words_f = Counter(f_list).most_common(n)
	rank = 0
	for w in top25Words_f:
		rank += 1
		print w[0], '\t\t', w[1], '\t\t', rank, '\t', probability(w[1], counterTotalWords(words)), '\t\t', rank * probability(w[1], counterTotalWords(words))




# return the probability of occurrence
def probability(occurs, total_quantity):
	return round(float(occurs)/total_quantity,4)




def main():
	with open('output.txt') as f:
		words = f.readlines()
		words = map(lambda f: f.strip(), words)
		f.closed
	Total_Words = counterTotalWords(words)
	Total_Uni_Words = countUniWords(words)
	print "The most frequent 25 words are as following:"
	print "Word", '\t' "Frequency", '\t', "Rank", '\t', "Probability", '\t', "Rank*Probability"
	topWords(words, 25)
	print "\n"
	print "\n"
	print "The most frequent 25 additional words that start with the letter f are as following:"
	print "Word", '\t\t' "Frequency", '\t', "Rank", '\t', "Probability", '\t', "Rank*Probability"
	visited = []
	for w in Counter(words).most_common(25):
		visited.append(w[0])
	topWord_f(words, 25, visited)
	print "Total Words:", Total_Words
	print "Total Unique Words:", Total_Uni_Words


main()











