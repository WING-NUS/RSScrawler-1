# -*- coding: utf-8 -*-
"""
Following explanation gives purposes of some files generated in the process :
1. rsscrawler.cfg store some options.
2. RSSName.db stores words frequency file generated from fetched web pages' title.
3. fileName.db (fileName means one RSS source link address) stores all links of web pages fetched in terms of one RSS link  source.
4. filename.html stores the whole webpage fetched, where filename is gotten by news' title. 
5. RSSName.txt stores words frequency file generated from fetched web pages' tilte.
"""

__author__ = "Fang Ning"
__date__ = "06.10.2012"
__version__ = "1.5.0"
__credits__ = """This code mainly complete to fetch all RSS news . 
You may freely use it in your project , but please remain the head's  information part.
"""
import logging
import feedparser
import shutil
import os
import os.path
import time
import datetime
import math
import urllib
import urllib2
import re
import fileinput
import sys, getopt
import codecs
import string
import sqlite3
import json
import ConfigParser
from urlparse import urlparse
import hashlib

from SpecialSites import SpecialSites
from newsextractor import NewsBlogExtractor

class rsscrawler:
	# every webpage fetched is stored in a specified html file in hard disk.
	# file name is its title, so we need to remove illegal chars from its title in order to consist with file name requirement.
	def replaceAll4FileName(self,oldName):
		dd = oldName.replace('http://','')
		dd = dd.replace('https://','')
		dd = dd.replace('/','.')
		dd = dd.replace('?', '.')
		dd = dd.replace(':', '.')
		dd = dd.replace('\\', '.')
		dd = dd.replace('\n', '.')
		dd = dd.replace('*', '.')
		dd = dd.replace('<', '.')
		dd = dd.replace('>', '.')
		dd = dd.replace('|', '.')
		dd = dd.replace('"', '.')
		return dd

	# load word frequency record from cnn.txt file
	def loadWordsFrequency (self):
		try:
			if not os.path.exists(self.ppath + self.RSSName+'_wordsfreq'+'.db'):
				conn = sqlite3.connect(self.ppath + self.RSSName+'_wordsfreq'+'.db')
				c = conn.cursor()

				# Create table
				c.execute('''CREATE TABLE wordsfreq (date text, source text, words text, frequency real)''')		
				c.close()
				return 'create success'
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
				return 'load success'
		except:
			return 'failed'
		# print wordsFreq

	# calculate word frequency
	def calWordsFrequency(self,content, daytime):
		text = content
		text = text.encode('utf-8')
		trans = string.maketrans(string.punctuation+"0123456789"," " * (len(string.punctuation)+10))
		text = string.translate(text, trans)   # strip out punct, digits
		text = text.lower()

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
		return self.wordsFreq

	# create all fetched links database file
	def createAllFetchedLinks(self,fileName):
		try:
			if not os.path.exists(self.ppath + fileName +'.db'):
				conn = sqlite3.connect(self.ppath + fileName +'.db')
				c = conn.cursor()
				# Create table
				c.execute('''CREATE TABLE links (link text)''')
				c.close()
		except:
			return 'failed'

	# determine duplication of fetched links
	def determineDuplication(self,fileName,link):
		try:
			conn = sqlite3.connect(self.ppath + fileName +'.db')
			c = conn.cursor()
			if type(link) is str:
				link=link.decode('utf-8')
			for a  in set(c.execute('SELECT link FROM links WHERE link = link')):
				if link == a[0]:
					c.close()
					return 'True'
			else:
				c.close()
				return 'False'
		except:
			return 'failed'

	# insert a new fetched link into database
	def updateNewLinks(self,fileName, newlink):
		try:
			conn = sqlite3.connect(self.ppath + fileName+'.db')
			c = conn.cursor()
			if type(newlink) is str:
				newlink=newlink.decode('utf-8')
			c.execute('INSERT INTO links VALUES (?)', (newlink,))
			conn.commit()
			c.close()
			return 'success'
		except:
			return 'failed'

	# fetch all images
	def fetchAllImages(self, images, webpage_link):
		for a in images.keys():
			time.sleep(0.001)
			file_id = int(time.time() * 1000)
			try:
				filehandle = urllib.urlopen(images[a]) # fetch an image 
				img = filehandle.read()
				link = filehandle.geturl()
				img_type = urlparse(link).geturl().split('?')[0].split('.').pop() # get type of image
				if img_type != 'png' and img_type !='jpg' and img_type !='gif':
					img_type = 'dynamic_img'
				# print "img_type = "+img_type
				try:
					img_filename = hashlib.md5(a).hexdigest()
				except:
					pass
			except :
				# logging.warning("there is a connection error for images")
				continue
			filehandle.close()

			try:
				myFile = open(self.sub_ppath  + str(file_id)+'.'+img_filename+'.'+"img", 'wb')
				myFile.write(img)
				data = {'webpage_link':webpage_link, 'original_link':a}
				content = json.dumps(data)
				new_line_img = str(file_id)+'.'+img_filename+'\t' + img_type + '\t'+ str(file_id)+ '\t'+ link + '\t' + link + '\t' + content + '\t' + '0' + '\t' + '-1'
				myFile2 = open(self.sub_ppath  + self.config['storagefile'], 'a')
				myFile2.write(new_line_img)
				myFile2.write('\n')
			except:
				# logging.warning("there is a storage error for images") 
				continue
			myFile.close()
			myFile2.close()

		return None


	# store new fetched links into MERGE.TXT and a whole webpage into .html file 
	def storeNewLinkInMERGEandHTML(self, file_id, rssResource, page, title, firstPage_link, link, page_num, date):
		try:
			file_name = hashlib.md5(title.encode('utf-8')).hexdigest()
		except:
			pass
		# print "file name = "+file_name
		try:
			myFile = open(self.sub_ppath  + str(file_id)+'.'+file_name+'.html', 'w')
			myFile.write(page)
			language = 'English'
			sourcename = self.RSSName
			if self.RSSName in self.config['multisource']:
				sourcename,language = SpecialSites.getNameAndLanguageFromResource(rssResource,sourcename,language)

			data =  { 'source':rssResource, 'language': language, 'sourcename':sourcename, 'firstPage_link':firstPage_link, 'page': page_num, 'title': title, 'timestamp-sec': date}
			content = json.dumps(data)
			new_line_webpage = str(file_id)+'.'+file_name+'.html'+'\t' + 'html'+'\t'+ str(file_id)+'\t' + link + '\t' + link + '\t' + content + '\t' + '0' + '\t' + '-1'
			myFile2 = open(self.sub_ppath  + self.config['storagefile'], 'a')
			myFile2.write(new_line_webpage)
			myFile2.write('\n')

		except UnicodeEncodeError:
			logging.warning("there is a UnicodeEncodeError")
			return 'unicode error'
		finally:
			myFile.close()
			myFile2.close()
		return None

	# words frequency file format is "date	source	words	frequency"
	def updateWordsFrequency(self):
		# update database , that is, RSSName_wordsfreq.db
		conn = sqlite3.connect(self.ppath + self.RSSName+'_wordsfreq'+'.db')
		c = conn.cursor()
		c.execute('DELETE FROM wordsfreq')
		for key, value in sorted(self.wordsFreq.iteritems(), key=lambda t: t[0]):
			for key2, value2 in sorted(value.iteritems(), key=lambda t: t[1], reverse=True):
					if type(key2) is str:
						key2=key2.decode('utf-8')
					try:
						c.execute('INSERT INTO wordsfreq VALUES (?,?,?,?)', (key, self.RSSName, key2, value2))
					except UnicodeDecodeError:
						logging.warning("words frequency database, there is a UnicodeDecodeError")
						continue
		conn.commit()
		c.close()

		# update wordfrequency file , that is, RSSName.txt
		myFile = codecs.open( self.ppath + self.RSSName+'.txt',encoding='utf-8', mode='w')
		for key, value in sorted(self.wordsFreq.iteritems(), key=lambda t: t[0]):
			for key2, value2 in sorted(value.iteritems(), key=lambda t: t[1], reverse=True):
					if type(key2) is str:
						key2=key2.decode('utf-8')
					try:
						line = key + '	' + self.RSSName + '	' + key2 + '	'+str(value2)
						myFile.write(line)
					 	myFile.write('\n')
					except UnicodeDecodeError:
						logging.warning(self.RSSName + ".txt file is written error")
						continue
		myFile.close()

	# process argments input
	def processArgs(self,argv):
		sourcesfile = ''
		stopwordsfile = ''
		try:
			opts, args = getopt.getopt(argv,"hn:i:s:")
		except getopt.GetoptError:
			sys.stderr.write('rsscrawler.py -n <timestamp.name> -i <sources file> [-s <stopwords file>] \n')
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				sys.stderr.write( 'rsscrawler.py -n <timestamp.name> -i <sources file> [-s <stopwords file>]\n')
				sys.exit()
			elif opt == '-n':
				self.RSSName = arg.split('.')[1]
				self.TimeStamp = arg.split('.')[0]
			elif opt == '-i':
				sourcesfile = arg
			elif opt =='-s':
				stopwordsfile = arg

		if self.RSSName == '':
			sys.stderr.write( 'Please input News sources name ...\n')
			sys.exit(3)
		sys.stdout.write( 'Input News name is : '+ self.RSSName+'\n')
		sys.stdout.write( 'Input sources is : '+ sourcesfile+'\n')
		sys.stdout.write( 'stopwords file is : '+ stopwordsfile+'\n')

		commandName = os.path.basename(os.path.abspath( __file__ ))
		self.current_path = os.path.abspath( __file__ ).replace(commandName,'')
		self.path = os.path.abspath( __file__ ).replace(commandName, self.RSSName+'/') 
		self.ppath = self.path.replace('\\','/') # process windows style into linux style
		self.sub_ppath = self.ppath+self.TimeStamp+'.'+self.RSSName+'/'

		if not os.path.exists(self.ppath): 
			os.makedirs(self.ppath)

		if not os.path.exists(self.sub_ppath): 
			os.makedirs(self.sub_ppath)

		# setup log file
		logging.basicConfig(filename=self.ppath+self.RSSName+'.log',level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

		# load config file , such as, time zone difference, words frequency , and storage file name
		conf = ConfigParser.RawConfigParser()
		conf.read(self.current_path + 'rsscrawler.cfg')
		self.config['timezonedifference'] = conf.getint("System", "timezonedifference")
		self.config['wordsFrequency'] = conf.get("System", "wordsFrequency")
		self.config['storagefile'] = conf.get("System", "storagefile")
		self.config['imagestorage'] = conf.get("System", "imagestorage")
		self.config['specialsites'] = eval(conf.get("Specialprocessing", "specialsites"))
		self.config['multisource'] = eval(conf.get("Specialprocessing", "multisource"))
		# print "wordsFrequency = " + str(self.config['wordsFrequency'])

		# load sourcefile
		try:
			# print "ppath = "+self.ppath+ sourcesfile
			myFile = open( self.current_path + sourcesfile, 'r')
			for line in myFile:
				string = line.strip(' ').replace('\t','').replace('\r','').replace('\n','')
				if string != '':
					self.sources.append(string)
		except IOError:
			sys.stderr.write( "Please input correct sourcesfile : " + sourcesfile + " is read error \n")
			sys.exit(4)
		finally:
			myFile.close()
		# print "sources = "+str(sources)

		# load stopwords file
		try:
			myFile = open(  self.current_path + stopwordsfile , 'r')
			for line in myFile:
				string = line.strip(' ').replace('\t','').replace('\r','').replace('\n','')
				if string != '':
					self.stopWords.append(string)
		except IOError:
			sys.stderr.write( "Please input correct stopwordsfile : " + stopwordsfile + " file is read error , so default stopwords has been used\n")
			self.stopWords = ['shall', 'applause', 'a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your']
		finally:
			myFile.close()
		# print "stopwords = "+str(stopWords)

	# fetch a XML from a RSS source 
	def fetchXML(self,rssResource):
		try:
			d = feedparser.parse(rssResource)
			if len(d.entries) == 0:
				raise 'there is a wrong url'
		except :
			logging.warning("there is a wrong url")
			return 'wrong url'
		return d

	# fetch a whole webpage
	def fetchWebpage(self, link):
		file_id = int(time.time() * 1000)
		try:
			filehandle = urllib.urlopen(link) # fetch a whole webpage according a link attribution in XML
			page = filehandle.read()
			# print 'page = '+page
			link = filehandle.geturl()
		except IOError:
			logging.warning("there is a connection error") 
			return None, link, file_id
		filehandle.close()
		return page,link, file_id


	# fetch all RSS sources in terms of one news site (a source file)
	def fetchNews(self):
		for rssResource in self.sources:
			# print "rssResource = "+rssResource
			new_links = []
			fileName = self.replaceAll4FileName(rssResource)

			self.createAllFetchedLinks(fileName)

			d = self.fetchXML(rssResource)
			if d == "wrong url":
				continue

			# fetch all items from a RSS source 
			for dd in d.entries:
				ex = NewsBlogExtractor()
				page_num = 1
				page, link, file_id= self.fetchWebpage(dd.link)
				firstPage_link = link
				while link != None:
					time.sleep(0.1)					
					# special processing for some RSS sources
					if self.RSSName in self.config['specialsites']:
						# page, link = globals()["SpecialSites." + self.RSSName](page, link)
						if self.RSSName == 'newyorktimes':
							page, link = SpecialSites.newyorktimes(page, link)
						elif self.RSSName == 'straitstimes':
							page, link = SpecialSites.straitstimes(page, link)

					if (page == None) or (len(page) == 0):
						break # next item

					if self.determineDuplication(fileName,link) == 'False':
						#  insert the new  link into database
						self.updateNewLinks(fileName, link)

						# store a new link in a special file , such as, MERGE.TXT, and store its whole webpage in a HTML file
						self.storeNewLinkInMERGEandHTML(file_id, rssResource, page, dd.title, firstPage_link, link, page_num, str(time.mktime(dd.published_parsed)+self.config['timezonedifference']*3600))

						# special processing for special sites
						language = 'English'
						sourcename = self.RSSName
						if self.RSSName in self.config['multisource']:
							sourcename,language = SpecialSites.getNameAndLanguageFromResource(rssResource,sourcename,language)

						# store all images in the webpage
						if rssinstance.config['imagestorage'] == "True":
							o = urlparse(link)
							images = ex.findAllImages(page, o.netloc, sourcename)
							# print images
							self.fetchAllImages(images, link)

						# calculate word frequency in title
						if self.config['wordsFrequency'] == "True":
							self.calWordsFrequency(dd.title, str(dd.published_parsed[2]))

						new_links.append(link)

						# process multiple pages
						link = ex.findNextPage(page, sourcename)
						if link != None:
							page_num +=1
							page, link,file_id = self.fetchWebpage(link)
					else:
						break

			if (len(new_links) !=0) :
				# update words frequency record file
				if self.config['wordsFrequency'] == "True":
					self.updateWordsFrequency()

			time.sleep(1)
		return None

	def __init__(self):

		# configaration
		self.config = {}

		# special processing
		self.specialsites =[]

		# RSS sources
		self.sources= []

		# count words by stop words table
		self.stopWords = []

		# give a path name to store webpages and links fetched
		self.RSSName ='' # store specifical directory name
		self.TimeStamp = '' # store specifical sub-directory name, format is "TimeStamp.RSSName"
		self.current_path = ''
		self.path = ''
		self.ppath = ''
		self.sub_ppath = ''

		# "wordsFreq" is used to count words that occur in a title .
		self.wordsFreq = {}

# Main function to fetch RSS sources
if __name__ == '__main__':
	# initiate an object
	rssinstance = rsscrawler()
	# read config file and process args
	rssinstance.processArgs(sys.argv[1:])
	# count words frequency from titles, if you donot need it, you may remove the following processing
	if rssinstance.config['wordsFrequency'] == "True":
		rssinstance.loadWordsFrequency()
	# get all RSS news webpages
	rssinstance.fetchNews()
