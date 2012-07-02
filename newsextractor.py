# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup

# [ matching pattern ]
__flags__ = { \
    'cnn': {'content':['p', 'class' , 'cnn_storypgraphtxt'], 'title':['h1'], 'date':['div','class','cnn_strytmstmp'], 'date_extract':['(\w+) ([0-9]{1,2}), ([0-9]{4})']}, \
    'economist': {'content':['id', 'id' , 'ec-article-body'], 'title':['h1'], 'date':['p','class','ec-article-info'], 'date_extract':['(\w+) ([0-9]{1,2})\w* ([0-9]{4})']}, \
    'foxnews': {'content':['div', 'class' , 'article-text'], 'title':['h1'], 'date':['p','class','published updated dtstamp'], 'date_extract':['Published (\w+) ([0-9]{1,2}), ([0-9]{4})']},  \
    'ibtimes': {'content':['id', 'id' , 'content'], 'title':['h1'], 'date':['p','class','story_on'], 'date_extract':['(\w+) ([0-9]{1,2}), ([0-9]{4}) ([0-9]{1,2}:[0-9]{1,2}) (\w+) (\w+)'], 'page':['http://www.ibtimes.com']}, \
    'newyorktimes': {'content':['p', 'itemprop' ,'articleBody'], 'title':['h1'], 'date':['h6','class','dateline'], 'date_extract':['Published: (\w+) ([0-9]{1,2}), ([0-9]{4})'], 'page':['http://www.nytimes.com'], 'image':['http://yoursdp.org']}, \
    'rfi': {'content':['div', 'class' , 'article-main-text'], 'title':['h1'], 'date':['div','class','article-header-date'], 'date_extract':['([0-9]{1,2}) (\w+) ([0-9]{4})$']}, \
    'smh': {'content':['div', 'class' , 'articleBody'], 'title':['h1'], 'date':['tag','tag','cite'], 'date_extract':['(\w+) ([0-9]{1,2}), ([0-9]{4})']}, \
    'straitstimes': {'content':['div', 'class' , 'storyRight'], 'title':['h1'], 'date':['div','class','published'], 'date_extract':['(\w+) ([0-9]{1,2}), ([0-9]{4})$']}, \
    'swissinfo': {'content':['div', 'class' , 'fl-l'], 'title':['h1'], 'date':['div','class','date grey-dark italic'], 'date_extract':['(\w+) ([0-9]{1,2}), ([0-9]{4}) - (\d+:\d+)']}, \
    'thesun': {'content':['id', 'id' , 'bodyText'], 'title':['h1'], 'date':['div','class','published-date-text'], 'date_extract':['\w+:  ([0-9]{1,2})\w* (\w+) ([0-9]{4})']}, \
    'irishsun': {'content':['tag', 'tag' , 'article'], 'title':['h2'], 'date':['irishsun', '',''], 'date_extract':['([0-9]{1,2})\w* (\w+), ([0-9]{4})$']}, \
    'dailymail': {'content':['id' , 'id' , 'js-article-text'], 'title':['h1'], 'date':['span','class','article-timestamp'], 'date_extract':['([0-9]{1,2}:[0-9]{1,2}) (\w+), ([0-9]{1,2})\w* (\w+) ([0-9]{4})$']}, \
    'guardian': {'content':['id' , 'id' ,'content'], 'title':['h1'], 'date':['tag','tag','time'], 'date_extract':['\w+ ([0-9]{1,2}) (\w+) ([0-9]{4}) ([0-9]{1,2}.[0-9]{1,2}) (\w+)']}, \
    'ananova': {'content':['div', 'class' , 'articleinner' ], 'title':['h1'], 'date':['div','class','meta'], 'date_extract':['([0-9]{1,2}) (\w+) ([0-9]{4}), ([0-9]{1,2}:[0-9]{1,2})']}, \
    'corkman': {'content':['div', 'class' , 'body' ], 'title':['head'], 'date':['p','class','published'], 'date_extract':['\w+ (\w+) ([0-9]{1,2}) ([0-9]{4})']}, \
    'ladyironchef':{'content':['id' , 'id' ,'contentleft'], 'title':['h1'], 'date':['p','class','date'], 'date_extract':['(\w+) ([0-9]{1,2}), ([0-9]{4})']}, \
    'noobcook': {'content':['div', 'class' , 'entry-content' ], 'title':['h1'], 'date':['p','class','headline_meta'], 'date_extract':['(\w+) ([0-9]{1,2}), ([0-9]{4})']}, \
    'vivawoman': {'content':['id', 'id' , 'content'], 'title':['h1'], 'date':['span','class','date published time'], 'date_extract':['([0-9]{1,2}) (\w+) ([0-9]{4})$']}, \
    'xuxiaoming': {'content':['div', 'id' , 'sina_keyword_ad_area2'], 'title':['h2'], 'date':['span','class','time SG_txtc'], 'date_extract':['\(([0-9]{4})-([0-9]{1,2})-([0-9]{1,2}) ([0-9]{1,2}:[0-9]{1,2}):[0-9]{1,2}\)']}, \
    'twocold': {'content':['div', 'id' , 'sina_keyword_ad_area2'], 'title':['h2'], 'date':['span','class','time SG_txtc'], 'date_extract':['\(([0-9]{4})-([0-9]{1,2})-([0-9]{1,2}) ([0-9]{1,2}:[0-9]{1,2}):[0-9]{1,2}\)']},\
    'jpost':{'content':['div', 'class' , 'body'], 'title':['h1'], 'date':['div','class','date'], 'date_extract':['([0-9]{1,2})/([0-9]{1,2})/([0-9]{4}) ([0-9]{1,2}:[0-9]{1,2})']}, \
    'channelnewsasia':{'content':['id', 'id' , 'articlecontent'], 'title':['head'], 'date':['p','class','header'], 'date_extract':['\w+: ([0-9]{1,2})\w* (\w+) ([0-9]{4})']}, \
    'bbc':{'content':['tag', 'tag' , 'p'], 'title':['h1'], 'date':['span','class','story-date'], 'date_extract':['([0-9]{1,2}) (\w+) ([0-9]{4}) \w+ \w+ \w+ ([0-9]{1,2}:[0-9]{1,2}) (\w+)']}, \
    'ynet':{'content':['id', 'id' , 'article_content'], 'title':['h1'], 'date':['p','style','margin-top:8'], 'date_extract':['([0-9]{1,2}).([0-9]{1,2}).([0-9]{1,2}), ([0-9]{1,2}:[0-9]{1,2})']}, \
    'newscomau':{'content':['div', 'class' , 'story-body  lead-media-none'], 'title':['h1'], 'date':['li','class','date-and-time  last'], 'date_extract':['(\w+) ([0-9]{1,2}), ([0-9]{4}) ([0-9]{1,2}:[0-9]{1,2})(\w+)']}, \
    'MissTamChiakSingaporeFoodBlogchinese' : {'content':['div', 'class' , 'post-body entry-content'], 'title':['h3'], 'date':['h2','class','date-header'], 'date_extract':['([0-9]{1,2}) (\w+), ([0-9]{4})']}, \
    'mrbrown' : {'content':['div', 'class' , 'entry-body'], 'title':['h3'], 'date':['h2','class','date-header'], 'date_extract':['\w+, (\w+) ([0-9]{1,2}), ([0-9]{4})']}, \
    'ieatishootipost':{'content':['div', 'class' , 'post-body entry-content'], 'title':['h3'], 'date':['a','class','timestamp-link'], 'date_extract':['\w+, (\w+) ([0-9]{1,2}), ([0-9]{4})']}, \
    'yawningbread':{'content':['div', 'class' , 'entry-content'], 'title':['h3'], 'date':['abbr','class','published'], 'date_extract':['([0-9]{1,2}) (\w+) ([0-9]{4})']}, \
    'yoursdp':{'content':['tag', 'tag' , 'p'], 'title':['head'], 'date':['td','class','createdate'], 'date_extract':['([0-9]{1,2}) (\w+) ([0-9]{4})']}, \
}

class Extract:
    def extract(self, stream, sourcename = None):
        if not __flags__.has_key(sourcename):
            return None
        res = __flags__[sourcename]
        
        if (sourcename == 'xuxiaoming' or sourcename == 'twocold'): # special for sina blog
            soup = BeautifulSoup(stream[:stream.find('<head>')] + stream[stream.find('<body>'):])
        else:
            soup = BeautifulSoup(stream)

        # remove script
        for script in soup("script"):
            soup.script.extract()

        # extract title
        try:
            if res['title'][0] == 'h1':
                title = soup.h1.get_text()
            elif res['title'][0] == 'h2': # special processing for irishsun
                title = soup.h2.get_text()
            elif res['title'][0] == 'h3': # special processing for MissTamChiakSingaporeFoodBlogchinese
                title = soup.h3.get_text()                
            elif res['title'][0] == 'head':  # special processing for channelnewsasia , corkman, yoursdp
                title = soup.html.head.title.string.split('-')[0]
            title = title.replace('\n',' ').replace('\t',' ').strip(' ')
        except:
            title = ''

        # extract date 
        try:
            if res['date'][0] == 'tag':
                data = soup.find(res['date'][2]).get_text()
                print "date = " + data
            elif res['date'][0] == 'id':
                # print "date = " + soup.find(id=res['date'][2]).get_text()
                data = soup.find(id=res['date'][2]).get_text()
            elif res['date'][0] == 'irishsun': # special for irishsun
                data =  soup.h2.findNextSibling('p').get_text()
                # print "date = " + data
            else:
                data = soup.find(res['date'][0], {res['date'][1]:res['date'][2]}).get_text()
                # print "data = "+ data
            data = data.replace('\n',' ').replace('\t',' ').strip(' ')

            date = re.search(res['date_extract'][0], data)
            if (sourcename == 'yoursdp' or sourcename == 'yawningbread' or sourcename == 'MissTamChiakSingaporeFoodBlogchinese' or sourcename == 'rfi' or sourcename == 'thesun' or sourcename == 'irishsun' or sourcename == 'vivawoman' or sourcename == 'channelnewsasia'): # e.g. 01 June 2012
                # print "111 = " + date.group(1) 
                t = (date.group(2) , date.group(1), date.group(3)) 
                new_date = str(t)
            elif sourcename == 'dailymail': # 14:21 GMT, 8 June 2012
                # print "222 = " + date.group(0)
                t = (date.group(4) , date.group(3), date.group(5),  date.group(1), date.group(2))
                new_date = str(t)
            elif sourcename == 'guardian': # 8 June 2012 19.47 BST
                t = (date.group(2) , date.group(1), date.group(3),  date.group(4).replace('.',':'), date.group(5))
                new_date = str(t) 
            elif sourcename == 'ananova': # 10 June 2012, 4:58
                t = (date.group(2) , date.group(1), date.group(3),  date.group(4))
                new_date = str(t)
            elif sourcename == 'xuxiaoming' or sourcename == 'twocold': # 2012-05-10 03:21:27
                t = (date.group(2) , date.group(3), date.group(1),  date.group(4))
                new_date = str(t)
            elif sourcename == 'bbc': # 22 June 2012 Last updated at 17:43 GMT
                t = (date.group(2) , date.group(1), date.group(3),  date.group(4), date.group(5))
                new_date = str(t)
            elif sourcename == 'ynet': #    06.22.12, 09:33
                t = (date.group(1) , date.group(2), '20'+date.group(3),  date.group(4))
                new_date = str(t)                                        
            else : # June 01 2012 10:20 AM GMT
                new_date = str(date.groups())
            # print new_date
        except:
            print "there is an error"
            new_date = ''

        # extract content
        try:
            if res['content'][0] == 'tag':
                contents=soup.findAll(res['content'][2])
            elif res['content'][0] == 'id':
                contents=soup.findAll(id=res['content'][2])
            elif res['content'][0] == 'div' or res['content'][0] == 'p':
                contents=soup.findAll(res['content'][0], {res['content'][1] : res['content'][2]})
            text = ''        
            for line in contents:
                text +=line.get_text()
            # print text.encode('utf-8')
        except:
            text = ''
        

        # Create an object to return
        # Note: the "maincontent" must exist

        extracted = {'maincontent': text, 'title':title, 'date':new_date}
        return extracted

    # merge multiple pages into one webpage
    def extractMore(self, pages, sourcename = None):
        text = ''
        for stream in pages:
            d = self.extract(stream, sourcename)
            text += d[maincontent]
            title = d[title]
            date = d[date]

        # Create an object to return
        # Note: the "maincontent" must exist

        extracted = {'maincontent': text, 'title':title, 'date':new_date}
        return extracted

    # find next page
    def findNextPage(self, page, sourcename = None):
            if not __flags__.has_key(sourcename):
                return None
            res = __flags__[sourcename]
            if not res.has_key('page'):
                return None
            soup = BeautifulSoup(page)
            link = soup.find('a', { "class" : "next" })
            if link != None and link['href'][0] == '/':
                return res['page'][0]+link['href']
            else:
                return None

    # findAllImages
    def findAllImages(self, page, netloc, sourcename = None):
        if not __flags__.has_key(sourcename):
            return None
        link_head = ''
        soup = BeautifulSoup(page)
        try:
            if soup.html.head.base.has_key('href'):
                link_head =soup.html.head.base['href'].strip(' ')
            else:
                link_head = netloc
        except:
            pass
            
        images = {}
        for x in soup.findAll('img'):
            link = x['src'].strip(' ')
            if link[:7] != 'http://':
                images[link] = link_head+link
            else:
                images[link] = link
        # print images
        return images

