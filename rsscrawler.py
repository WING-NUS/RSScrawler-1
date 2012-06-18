# -*- coding: utf-8 -*-
"""
Following explanation gives purposes of some files generated in the process :
1. RSSName.db stores words frequency file generated from fetched web pages in order to visualize words trends of News API.
2. fileName.db (fileName means one RSS source link address) stores all links of web pages fetched in terms of one RSS link  source.
3. MERGE.TXT stores updated links, title, source, and date of web pages fetched from last commit  in terms of one News source, such as CNN News.
4. filename.html stores the whole webpage fetched, where filename is gotten by news' title. 
"""

__author__ = "Fang Ning"
__date__ = "06.10.2012"
__version__ = "1.5.0"
__credits__ = """This code mainly complete to fetch all RSS news . 
You may freely use it in your project , but please remain the head's  information part.
"""

import feedparser
#import tag
import shutil
import os
import os.path
import time
import datetime
import math
import urllib
import re
import fileinput
import sys, getopt
import codecs
import string
import sqlite3
import json
class rsscrawler:
	# every webpage fetched is stored in a specified html file in hard disk.
	# Its name is its title, so we need to remove illegal chars from its title in order to consist with file name requirement.
	def replaceAll4FileName(self,oldName):
		dd = oldName.replace('http://','')
		dd = dd.replace('https://','')
		dd = dd.replace('/',' ')
		dd = dd.replace('?', ' ')
		dd = dd.replace(':', ' ')
		dd = dd.replace('\\', ' ')
		dd = dd.replace('\n', ' ')
		dd = dd.replace('*', ' ')
		dd = dd.replace('<', ' ')
		dd = dd.replace('>', ' ')
		dd = dd.replace('|', ' ')
		dd = dd.replace('"', ' ')
		return dd

	# load word frequency record from cnn.txt file
	def loadWordsFrequency (self):
		if not os.path.exists(self.ppath + self.RSSName+'_wordsfreq'+'.db'):
			conn = sqlite3.connect(self.ppath + self.RSSName+'_wordsfreq'+'.db')
			c = conn.cursor()

			# Create table
			c.execute('''CREATE TABLE wordsfreq (date text, source text, words text, frequency real)''')		
			c.close()
		else:
			conn = sqlite3.connect(self.ppath + self.RSSName+'_wordsfreq'+'.db')
			c = conn.cursor()
			for line in c.execute('SELECT * FROM wordsfreq'):
				if line[0] not in self.wordsFreq.keys():
					self.wordsFreq[line[0]]={line[2]:int(line[3])}
				elif line[2] not in self.wordsFreq[line[0]].keys():
					self.wordsFreq[line[0]][line[2]] = int(line[3])
				else:
					self.wordsFreq[line[0]][line[2]] += int(line[3])
			c.close()			

		# print wordsFreq

	# stemming terms by lib, return a List of terms
	"""
	def stemmingTerms(self,content):
		results = []
		tagger = tag.Tagger()
		tagger.initialize()
		#tagger.tokenize(content)
		for term in tagger(content):
			results.append(term[2])
		return results
	"""

	# calculate word frequency
	def calWordsFrequency(self,content, daytime):
		text = content
		text = text.encode('utf-8')
		trans = string.maketrans(string.punctuation+"0123456789"," " * (len(string.punctuation)+10))
		text = string.translate(text, trans)   # strip out punct, digits
		text = text.lower()

		#text = string.replace(text, '\n', ' ').strip('\n ')
		#words = stemmingTerms(text)
		words = string.replace(text, '\n', ' ').strip('\n ').split(' ')

		words = [w for w in words if len(w)>1] # ignore I, A, etc...

		if ( daytime not in set(self.wordsFreq.keys())):
			self.wordsFreq[daytime] = {}
		for word in words:
			if (word not in set(self.stopWords)):
				if (len(self.wordsFreq[daytime].keys()) == 0) or (word not in set(self.wordsFreq[daytime].keys())):
					self.wordsFreq[daytime][word] = 1
				else:
					self.wordsFreq[daytime][word] += 1

	# load all fetched links from .db file
	def loadAllFetchedLinks(self,fileName):
		links = []
		if not os.path.exists(self.ppath + fileName +'.db'):
			conn = sqlite3.connect(self.ppath + fileName +'.db')
			c = conn.cursor()
			# Create table
			c.execute('''CREATE TABLE links (link text)''')
			c.close()
		else:
			conn = sqlite3.connect(self.ppath + fileName +'.db')
			c = conn.cursor()
			for line in c.execute('SELECT * FROM links'):
				# print line[0]
				links.append(line[0])
			c.close()
		# print links
		return links

	# update new fetched links into .db file
	def updateNewLinks(self,fileName, newlinks):
		conn = sqlite3.connect(self.ppath + fileName+'.db')
		c = conn.cursor()
		for line in newlinks:
			#print line
			if type(line) is str:
				line=line.decode('utf-8')
			c.execute('INSERT INTO links VALUES (?)', (line,))
		conn.commit()
		c.close()

	# for give some parameters in MERGE.TXT
	def getNameAndLanguageFromResource(self,rssResource):
		if self.RSSName == "blog-en" : 
			if rssResource == "http://feeds.feedburner.com/VivaWoman":
				name = "vivawoman"
				language = "English"
			elif rssResource == "http://feeds2.feedburner.com/Noobcookcom":
				name = "noobcook"
				language = "English"
			elif rssResource == "http://www.ladyironchef.com/feed/":
				name = "ladyironchef"
				language = "English"
		elif self.RSSName == "blog-cn":
			if rssResource == "http://blog.sina.com.cn/rss/1300871220.xml":
				name = "xuxiaoming"
				language = "Chinese"
			elif rssResource == "http://blog.sina.com.cn/rss/1191258123.xml":
				name = "twocold"
				language = "Chinese"
		else:
			name = self.RSSName
			language = "English"
		return (name,language)	

	# store new fetched links into MERGE.TXT and a whole webpage into .html file 
	def storeNewLinkInMERGEandHTML(self,rssResource, page, title, link, date):
		dd = self.replaceAll4FileName(title)
		file_id = int(time.time() * 1000)
		# print "ppath = "+self.ppath
		try:
			myFile = open(self.ppath  + str(file_id)+'.'+dd+'.html', 'w')
			myFile.write(page)
			(sourcename,language) = self.getNameAndLanguageFromResource(rssResource)
			data =  { 'source':rssResource, 'language': language, 'sourcename':sourcename, 'page': 1, 'title': title, 'date': date}
			content = json.dumps(data)
			new_line = str(file_id)+'.'+dd.encode('utf-8')+'.html '+'	' + link + '	' + link + '	' + content + '	' + '0' + '	' + '-1'
			myFile2 = open(self.ppath  + 'MERGE.TXT', 'a')
			myFile2.write(new_line)
			myFile2.write('\n')
		except UnicodeEncodeError:
			print "there is a UnicodeEncodeError  ..."
			return "error"
		finally:
			myFile.close()
			myFile2.close()

	# words frequency file format is "date	source	words	frequency"
	def updateWordsFrequency(self):
		conn = sqlite3.connect(self.ppath + self.RSSName+'_wordsfreq'+'.db')
		c = conn.cursor()
		c.execute('DELETE FROM wordsfreq')
		for key, value in sorted(self.wordsFreq.iteritems(), key=lambda t: t[0]):
			for key2, value2 in sorted(value.iteritems(), key=lambda t: t[1], reverse=True):
					# if value2 <3:
					# 	continue
					# print 	key, RSSName, key2, value2
					# print "key2 = "+key2 
					if type(key2) is str:
						key2=key2.decode('utf-8')
					try:
						c.execute('INSERT INTO wordsfreq VALUES (?,?,?,?)', (key, self.RSSName, key2, value2))
					except UnicodeDecodeError:
						print "words database, there is a UnicodeDecodeError  ..."
						# print "111 " + key, RSSName, key2, value2
						continue
		conn.commit()
		c.close()

		myFile = codecs.open( self.ppath + self.RSSName+'.txt',encoding='utf-8', mode='w')
		# first_line = str('daytime' + '	' + 'source' + '	' + 'words' + '	' + 'frequency')
		# myFile.write(first_line.decode('utf-8'))
		# myFile.write('\n'.decode('utf-8'))

		for key, value in sorted(self.wordsFreq.iteritems(), key=lambda t: t[0]):
			for key2, value2 in sorted(value.iteritems(), key=lambda t: t[1], reverse=True):
					# if value2 <3:
					# 	continue
					if type(key2) is str:
						key2=key2.decode('utf-8')
					try:
						line = key + '	' + self.RSSName + '	' + key2 + '	'+str(value2)
						myFile.write(line)
					 	myFile.write('\n')
					except UnicodeDecodeError:
						print self.RSSName+ ".txt file is written error ..."
						# print 	"222 " + key, RSSName, key2, value2
						continue
		myFile.close()

	# process argments input
	def processArgs(self,argv):
		sourcesfile = ''
		stopwordsfile = ''
		try:
			opts, args = getopt.getopt(argv,"hn:i:s:")
		except getopt.GetoptError:
			print 'rsscrawler.py -n <news name> -i <sources file> [-s <stopwords file>] '
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				print 'rsscrawler.py -n <news name> -i <sources file> [-s <stopwords file>]'
				sys.exit()
			elif opt == '-n':
				self.RSSName = arg
			elif opt == '-i':
				sourcesfile = arg
			elif opt =='-s':
				stopwordsfile = arg

		# print "flag_newyorktimes = "+ str(flag_newyorktimes)

		if self.RSSName == '':
			print 'Please input News sources name ...'
			sys.exit(3)
		print 'Input News name is : ', self.RSSName
		print 'Input sources is : ', sourcesfile
		print 'stopwords file is : ', stopwordsfile

		commandName = os.path.basename(os.path.abspath( __file__ ))
		self.path = os.path.abspath( __file__ ).replace(commandName, self.RSSName+'/') 
		self.ppath = self.path.replace('\\','/') # distinguish windows from linux system

		try:
			myFile = open( self.ppath + sourcesfile, 'r')
			for line in myFile:
				string = line.strip(' ').replace('\t','').replace('\r','').replace('\n','')
				if string != '':
					self.sources.append(string)
		except IOError:
			print "Please input correct sourcesfile : " + sourcesfile + " is read error ..."
			sys.exit(4)
		finally:
			myFile.close()
		# print "sources = "+str(sources)

		try:
			myFile = open( os.path.abspath( __file__ ).replace('\\','/').replace(commandName, stopwordsfile) , 'r')
			for line in myFile:
				string = line.strip(' ').replace('\t','').replace('\r','').replace('\n','')
				if string != '':
					self.stopWords.append(string)
		except IOError:
			print "Please input correct stopwordsfile : " + stopwordsfile + " is read error ... , so default stopwords has been used"
			self.stopWords = ['shall', 'applause', 'a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your']
		finally:
			myFile.close()
		# print "stopwords = "+str(stopWords)

	# fetch all RSS sources in terms of one news site (a source file)
	def fetchNews(self):
		for rssResource in self.sources:
			# print "rssResource = "+rssResource
			new_links = []
			fileName = self.replaceAll4FileName(rssResource)

			links = self.loadAllFetchedLinks(fileName)

			# feedparser lib is used to parse XML file from a RSS source 
			d = feedparser.parse(rssResource)

			#print "d = " +str(d)
			if len(d.entries) == 0:
				print "there is a rss source error ..."
				continue

			# fetch all items from a RSS source 
			i = -1
			while 1:
				time.sleep(0.1)
				i = i+1
				try:
					if (self.RSSName == 'newyorktimes' ) : # solve redirect problem in terms of NewYork Times RSS webpage fetching
						while 1:
							try:
								filehandle = urllib.urlopen(d.entries[i].link) # fetch a whole webpage according a link attribution in XML
								page = filehandle.read()
								# print 'page = '+page
								d.entries[i].link = filehandle.geturl() # solve redirect problem of webpage to get real link address	
								# print "link = "+d.entries[i].link					
								if len(page) == 0 and (d.entries[i].link.find("http://www.nytimes.com/glogin?URI=") != -1):
									d.entries[i].link = d.entries[i].link.replace("http://www.nytimes.com/glogin?URI=","").split('&')[0]
								else:
									break
							except IOError:
								print "there is a connection error ..."
								break
							finally:
								filehandle.close()
					else:
						try:
							filehandle = urllib.urlopen(d.entries[i].link) # fetch a whole webpage according a link attribution in XML
							page = filehandle.read()
							# print 'page = '+page
							d.entries[i].link = filehandle.geturl()
						except IOError:
							print "there is a connection error ..."
							continue
						finally:
							filehandle.close()					

					if (len(page) == 0):
						continue
					
					if d.entries[i].link not in links:
						
						# if find a new link , then store it in MERGE.TXT in corresponding format and store a whole webpage in a HTML file
						value = self.storeNewLinkInMERGEandHTML(rssResource, page, d.entries[i].title, d.entries[i].link, str(d.entries[i].published_parsed))
						# if (value == "error"):
						# 	continue
						# calculate words frequency
						self.calWordsFrequency(d.entries[i].title, str(d.entries[i].published_parsed[2]))

						new_links.append(d.entries[i].link)
						links.append(d.entries[i].link)

				except IndexError:
					print "there is no more items ..."
					break

			if (len(new_links) !=0) :
				# update all new  links into a db file
				self.updateNewLinks(fileName, new_links)

				# update words frequency record file
				self.updateWordsFrequency()

			time.sleep(1)

	def __init__(self):
		# determine special RSS source 
		self.flags = ['newyorktimes', 'economist']

		# RSS sources
		self.sources= []

		# count words by stop words table
		self.stopWords = []

		# get the path name to store fetech webpage and record feteched links, that is, ./cnn/ is its correct path
		self.RSSName =''
		self.path = ''
		self.ppath = ''

		# "wordsFreq" is used to count words that occur in a title .
		self.wordsFreq = {}

# Main function to fetch RSS sources
if __name__ == '__main__':
	rssinstance = rsscrawler()
	rssinstance.processArgs(sys.argv[1:])
	rssinstance.loadWordsFrequency()
	rssinstance.fetchNews()
