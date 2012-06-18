import unittest
import rsscrawler

class TestRSSCrawlerFunctions(unittest.TestCase):

	def setUp(self):
		self.instance = rsscrawler.rsscrawler()
		# test 15 sources
		self.instance.sources = ['http://feeds.foxnews.com/foxnews/entertainment','http://rss.cnn.com/rss/edition.rss','http://web.orange.co.uk/ice_article/feed.php?channel=news_home&format=rss','http://blog.sina.com.cn/rss/1191258123.xml','http://feeds.feedburner.com/VivaWoman','http://www.corkman.ie/news/rss','http://www.dailymail.co.uk/home/index.rss','http://www.economist.com/rss/the_world_this_week_rss.xml','http://feeds.guardian.co.uk/theguardian/rss','http://feeds.feedburner.com/IbtimescomWorld?format=xml','http://www.irishsun.com/index.php/id/aba4168066a10b8d/headlines.xml','http://www.english.rfi.fr/last_24h/rss','http://feeds.smh.com.au/rssheadlines/top.rss','http://www.straitstimes.com/STI/STIFILES/rss/mostreadstories.xml','http://www.swissinfo.org/eng/rss/front/index.xml','http://www.thesun.co.uk/sol/homepage/rss/' ]
		# count words by stop words table
		self.instance.stopWords = ['shall', 'applause', 'a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your']

		self.instance.RSSName ='test'
		self.instance.path = ''
		self.instance.ppath = ''

		# "wordsFreq" is used to count words that occur in a title .
		self.instance.wordsFreq = {}

	def test_fetchNews(self):		
		self.instance.fetchNews()
		# should raise an exception 
		self.assertRaises(TypeError, self.instance.fetchNews(), (1,2,3))

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestRSSCrawlerFunctions)
	unittest.TextTestRunner(verbosity=2).run(suite)