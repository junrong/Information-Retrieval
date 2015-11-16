#!/usr/bin/python

## global varibles
num_processed = 0	# number of words processed
num_uniq_seen = 0  # number of unique words seen
seen = []  # a list keep track of the words have been seen
pairs = []  # initialize the list of pair (number of words processed, number of unique words seen)


#######################################################################
## read the text
with open('output.txt') as f:
	words = f.readlines()  # read file line by line into list "words"
	words = map(lambda s: s.strip(), words) # remove the "\n" for every element in the list
	f.closed

###############################################################
## generate the list of (number of words processed, number of unique words seen) pairs
for w in words:
	num_processed += 1  # number of processed words add 1
	if w not in seen:
		num_uniq_seen += 1 # number of unique words seen add 1
		seen.append(w)  # add this word to seen
		pairs.append([num_processed,num_uniq_seen])  # append this pair to pairs
		
		
#######################################################################
## compute the K and beta, using least square method

x_sum = 0
y_sum = 0
LENGTH = len(pairs)
numerator = 0
denominator = 0

# compute the average value of x in coordinate pairs (x,y)
for p in pairs:
	x_sum += p[0]
x_avg = float(x_sum) / LENGTH  # compute the average value of x in coordinate pairs (x,y)

# compute the average value of y in coordinate pairs (x,y)
for p in pairs:
	y_sum += p[1]
y_avg = float(y_sum) / LENGTH  # compute the average value of y in coordinate pairs (x,y)
		
# compute the numberator 
for p in pairs:
	numerator += (p[0] - x_avg) * (p[1] - y_avg)
	
# compute the denominator
for p in pairs:
	denominator += (p[0] - x_avg)**2
	
# compute the slope
slope = float(numerator) / denominator

# compute the y-intercept
y_intercept = (y_avg - slope * x_avg)
	
print "v: ", num_uniq_seen
print "n: ", x_sum
print "beta: {0:.3f}".format(slope)
print "K: {0:.3f}".format(y_intercept)



