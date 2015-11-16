#!/usr/bin/python
# -*- coding: utf-8 -*- 


	
def main():
	total_words = 0
	total_uni_words = 0
	visited_words = []
	processed_words = []

	with open('output.txt') as f:
		words = f.readlines()
		words = map(lambda s: s.strip(), words)
		f.closed

	for w in words:
		total_words += 1
		if w not in visited_words:
			total_uni_words += 1
			visited_words.append(w)
			processed_words.append([total_words,total_uni_words])

	
	LEN = len(processed_words)
	x_sum = 0
	for w in processed_words:
		x_sum += w[0]
	x_avg = float(x_sum) / LEN
	y_sum = 0
	for w in processed_words:
		y_sum += w[1]
	y_avg = float (y_sum) / LEN

	numerator = 0
	for w in processed_words:
		numerator += (w[0] - x_avg) * (w[1] - y_avg)
	denominator = 0
	for w in processed_words:
		denominator += (w[0] - x_avg) ** 2
	beta = float(numerator)/ denominator
	k = (y_avg - beta * x_avg)

	print "the total number of unique number is v:", total_uni_words
	print "the total number of words in Alice.txt is n:", x_sum
	print "the beta is : {0:.3f}".format(beta)
	print "the k is : {0:.3f}".format(k)

main()


