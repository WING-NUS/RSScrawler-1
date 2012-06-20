# -*- coding: utf-8 -*-
import urllib

# [ flag initiate multi-blogs' source in one directory, give extractor function parameter that is, sourcename , language ]
__flags__ = { \
	'http://feeds.feedburner.com/VivaWoman': ['vivawoman', 'English' ], \
	'http://feeds2.feedburner.com/Noobcookcom': ['noobcook', 'English' ], \
	'http://www.ladyironchef.com/feed/': ['ladyironchef', 'English' ], \
	'http://blog.sina.com.cn/rss/1300871220.xml': ['xuxiaoming', 'Chinese'], \
	'http://blog.sina.com.cn/rss/1191258123.xml': ['twocold', 'Chinese' ]
}

class SpecialSites:
	# special processing for some RSS sources
	@staticmethod
	def newyorktimes(page,link):
		if ((page == None) and (link.find("http://www.nytimes.com/glogin?URI=") != -1)): # special processing of NewYork Times RSS webpage fetching
			link = link.replace("http://www.nytimes.com/glogin?URI=","").split('&')[0]
			try:
				filehandle = urllib.urlopen(link)
				page = filehandle.read()
				link = filehandle.geturl()
			except IOError:
				logging.warning("there is a connection error")
				return None,link
			finally:
				filehandle.close()
		return page,link

	@staticmethod	
	def straitstimes(page,link):
		if (link.find("http://sphreg.asiaone.com:80/RegAuth2/stpLogin.html") != -1):
			return None,link
		return page,link

	# get some parameters for storage file, that is, MERGE.TXT
	@staticmethod
	def getNameAndLanguageFromResource(rssResource,sourcename,language):
		# Since all Chinese blogs are stored into only one directory, some parametres of extractor function are required to get, that is, sourcename. Likewise to English blogs
		if not __flags__.has_key(rssResource):
			return sourcename,language
		res = __flags__[rssResource]
		return res[0],res[1]