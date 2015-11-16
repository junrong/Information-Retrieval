#!/usr/bin/python

from bs4 import BeautifulSoup
from collections import deque
import urllib2
import urlparse
import robotparser
import httplib
import time
import codecs
import re
from sets import Set


root = "http://www.ccs.neu.edu"
initialFrontier = deque([root])




def isValidLink(url):
	if not url: return False
	host = urlparse.urlparse(url).hostname
	domainValid = re.compile(r'.*\.neu.edu|\.northeastern.edu')
	if not domainValid.match(url): return False
 
	if not isDesiredContentType(url): return False

	rp = urlparse.urlsplit(url)
	parsedUrl = rp.geturl()
	return len(parsedUrl) > 0


def urlCrawl(url):
	hdr = {'User-Agent':'Mozilla/5.0'}
	req = urllib2.Request(url,headers=hdr)
	web = urllib2.urlopen(req)
	data = web.read()
	web.close()
	soup = BeautifulSoup(data)
	urlSet =set()
	for elt in soup.find_all('a'):
		link = elt.get('href')
		if isValidLink(link):
			urlSet.add(link)
	return urlSet




def isAllowedCrawl(url):
	robotparser.URLopener.version = "Mozilla/5.0"
	DOMAIN_NAME = "neu.edu"
	parser = robotparser.RobotFileParser()
	parser.set_url("http://www.ccs.neu.edu/robots.txt")
	parser.read()
	return parser.can_fetch(DOMAIN_NAME, url)




def isDesiredContentType(url):
	conn = httplib.HTTPConnection("www.ccs.neu.edu")
	connRequest = conn.request("GET", url)
	connRespense = conn.getresponse()
	return ('text/html' in connRespense.getheader('Content-Type') 
		or 'application/pdf' in connRespense.getheader('Content-Type'))
	



def crawlerThread(frontier):
	count = 0
	output = codecs.open("result.txt", 'w', "utf-8")
	visitedUrl = set() 
	while not len(frontier)==0 and count < 100: 
		url = frontier.popleft()
		if url not in visitedUrl and isDesiredContentType(url) and isAllowedCrawl(url):	# if website permit crawling regarding robots.txt
		    visitedUrl.add(url) 
		    count += 1
		    #time.sleep(5) 
		    links = urlCrawl(url)
		    output.write(url + ' ')
		    validURL = set()
		    for link in links:
		    	if isValidLink(link):
		    		validURL.add(link)

		    frontier.extend(validURL)

		    for link in validURL:
		    	output.write(link + ' ')
		    if count < 100: output.write('\n')

crawlerThread(initialFrontier)



