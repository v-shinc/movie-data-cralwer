#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'


import urllib
import urllib2
import random
import json
import sys
import sched, time
import cookielib
import os
import re
import datetime
from xlutils.copy import copy
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
from xlutils.copy import copy
import xlrd
import xlwt
import logging
logging.basicConfig(filename='../data/08_05.log',format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)



START_HTML = r"http://movie.douban.com/subject/24753811/"
def get_website(url):
    data = None
    try:
        # proxy_support = urllib2.ProxyHandler({'http':'http://211.167.112.14:80'})
        # opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        # urllib2.install_opener(opener)
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        data = res.read()
    except urllib2.URLError:
        print url ,"=>","an error occurs"
    finally:
        return data
visited = []
link_stack = []

def parse_html(html):
    movie = None
    if html == None:
        return None
    # try:
    soup = BeautifulSoup(html)

    if not re.compile('<span class="pl">集数:</span>').findall(html) == []:
        logging.info("This is not a movie")
        return None
    title = soup.head.title.contents[0].strip()
    title = title[:title.rindex('(')].strip()
    # title = p0.match(title).group('title')
    print title
    # get directors
    director_tags = soup.select('div #info > span > a[rel="v:directedBy"]')
    p1 = re.compile(r'<[^>]+>(?P<director>[^<]+)</a>')
    # print director_tags
    directors = [p1.match(str(t)).group('director') for t in director_tags]

    # get stars
    star_tags = soup.select('div #info > span > a[rel="v:starring"]')

    p2 = re.compile(r'<[^>]+>(?P<star>[^<]+)</a>')
    actors = [p2.match(str(t)).group('star') for t in star_tags]

    # get genre
    genre_tags = soup.select('div #info > span[property="v:genre"]')
    p3 = re.compile(r'<span property="v:genre">(?P<genre>[^<]+)</span>')
    genres = [p3.match(str(t)).group('genre') for t in genre_tags]

    # get release date
    pubdate_tag = soup.select('div #info > span[property="v:initialReleaseDate"]')
    # print pubdate_tag
    if pubdate_tag == []:
        return None
    # [0-9]{4}(-[0-9]{1,2}){0,1}(-[0-9]{1,2}){0,1}
    # p41 = re.compile(r'<[^>]+>(?P<pubdate>[^(]+)[(]([\u4e00-\u9fa5]+\/)*中国大陆(\/[\u4e00-\u9fa5]+)*([ ]3D)*[)]<[^>]+>')
    # p42 = re.compile(r'<[^>]+>(?P<pubdate>[^(]+)[(]([\u4e00-\u9fa5]+\/)*中国内地(\/[\u4e00-\u9fa5]+)*([ ]3D)*[)]<[^>]+>')
    # p43 = re.compile(r'<[^>]+>(?P<pubdate>[^(]+)[(]([\u4e00-\u9fa5]+\/)*香港(\/[\u4e00-\u9fa5]+)*([ ]3D)*[)]<[^>]+>')
    p41 = re.compile(r'<[^>]+>(?P<pubdate>[^(]+)[(]中国大陆([ ]3D)*[)]<[^>]+>')
    p42 = re.compile(r'<[^>]+>(?P<pubdate>[^(]+)[(]中国内地([ ]3D)*[)]<[^>]+>')
    p43 = re.compile(r'<[^>]+>(?P<pubdate>[^(]+)[(]香港([ ]3D)*[)]<[^>]+>')
    p44 = re.compile(r'[0-9-]+')
    f4 = 0
    for t in pubdate_tag:
        m = p41.search(str(t))
        if m != None:
            f4 = 1
            pubdate = m.group('pubdate')
            break
        m = p42.search(str(t))
        if m != None:
            f4 = 1
            pubdate = m.group('pubdate')
            break
        m = p43.search(str(t))
        if m != None:
            f4 = 1
            pubdate = m.group('pubdate')
            break
        m = p44.search(str(t))
        if m != None:
            f4 = 1
            pubdate = m.group()
            break
    if f4 == 0:
        logging.critical('{0} has no release date'.format(title))
        pubdate = None


    # get wishes
    wishes_tags = soup.select('div #subject-others-interests > .subject-others-interests-ft > a')
    # print wishes_tags
    if len(wishes_tags) == 0:
        return None
    # print wishes_tag
    m = re.match(r'<a href="http://movie.douban.com/subject/[0-9]+/wishes">(?P<wishes>[0-9]+)人想看</a>',str(wishes_tags[-1]))
    if m == None:
        logging.info('{0} has no wish'.format(title))
        wishes = None
    else:
        wishes = m.group('wishes')
    # id = m.group('id')

    movie = {}
    # movie['id'] = id
    movie['title'] = title
    movie['wishes'] = wishes
    movie['actors'] = actors
    movie['directors'] = directors
    movie['release'] = pubdate
    movie['genre'] = genres
    # except IOError as e:
    #     print "IOError", e.errno, e.strerror
    # except IndexError as e:
    #     print "IndexError",e.message
    # except KeyError as e:
    #     print "KeyError", e.message
    # finally:
    return movie


movies = {}
def crawl(html):

    movie = parse_html(html)
    # print movie
    if not movie == None:
        movies[movie['id']] = movie
    else:
        print None

    p5 = re.compile(r'<a href="(?P<address>http://movie.douban.com/subject/[0-9]+/[?]from=subject-page)" >')
    links = p5.findall(html)
    p6 = re.compile('http://movie.douban.com/subject/(?P<id>[0-9]+)/[?]from=subject-page')
    # print links
    urls = []
    for l in links:
        idd = p6.match(str(l)).group('id')
        if not idd in visited:
            visited.append(idd)
            urls.append(l)
    return urls

TMP = '../tmp.json'
def crawler(depth,url):
    if depth > 2:
        return
    html = get_website(url)
    if html == None:
        return
    next_urls = crawl(html)
    for link in next_urls:
        crawler(depth + 1, link)
    if depth == 0:
        f = open(TMP, 'w')
        f.write(unicode(json.dumps(movies, indent=4, ensure_ascii=False, encoding='utf8')))
        f.close()

def get_visited(inputs):
    v = []
    for input in inputs:
        movies = json.load(file(input))
        v.extend(movies.keys())
    v = [str(t) for t in v]
    return v

def merge(inputs,output):
    movies = {}
    for i in inputs:
        m = json.load(file(i))
        for k,v in m.items():
            movies[k] = v
            # if k in movies:
            #     old = movies[k]
            #     for nk,nv in

    f = open(output,'w')
    f.write(json.dumps(movies,indent= 4,ensure_ascii= False))
    f.close()

# Excel的格式：A电影名 B票房 C人数 D场次 5豆瓣url 6豆瓣中的电影名 7中国首映日期（人工纠正）
def download_by_url_crawler(execel_path,database_path):
    excel = xlrd.open_workbook(execel_path)
    sheet = excel.sheets()[0]
    urls = sheet.col_values(4)

    for u in urls:
        if not u == "":
            crawler(0,u)
            merge([TMP,database_path],database_path)


def extract_year(date):
    p = re.compile(r'[0-9]{4}')
    y = p.match(date)
    if not y == None:
        return y.group()
    return 0

# 根据excel导入的链接爬取豆瓣电影元数据
# excel_path：电影票房文件，格式为：A电影名 B票房 C人数 D场次 E豆瓣url F豆瓣中的电影名 G中国首映日期（人工纠正）
# target_path:导出json文件的路径
# database_path: 如果有database_path (json) ,则把database_path中的电影合并到target_path中去
# H列为-1表示要从豆瓣重新下载元数据
def download_by_url(execel_path,target_path,database_path = None):
    logging.info('START LOGGING FROM douban_movie_crawler.py')
    book = xlrd.open_workbook(execel_path)
    wbook = copy(book)
    movies = {}
    j = 5
    for iidx,sheet in enumerate(book.sheets()[:1]):
        print iidx
        urls = sheet.col_values(4)
        title = sheet.col_values(0)
        wsheet = wbook.get_sheet(iidx)
        year = sheet.name
        print year
        k = -1
        # H列标记是否要从豆瓣下载元数据
        if sheet.ncols < 8:
            continue
        flag = sheet.col_values(7)
        for idx, u in enumerate(urls):
            k += 1
            # logging.info('Name in 58921: '+ title[k])  # check the consistency of urls and movies
            if str(flag[idx]) == '':
                continue
            if not u == "":
                html = get_website(u)
                # time.sleep(random.randint(0,2))
                movie = parse_html(html)
                # print movie
                if u == 'not found':
                    continue
                id = re.search('[0-9]+',u).group()
                if not movie == None:
                    movies[id] = movie
                    wsheet.write(k,5,movie['title'])
                    print title[k],movie['title']
                    if not movie['title'] == title[k]:
                        logging.info('Name in 58921: {0}  Name in douban: {1}'.format(title[k],movie['title']))
                    if movie['release']!= None and str(extract_year(movie['release'])) != year:
                        logging.warning('%s: %s release date may be wrong' % (title[k], u))
                    print movie['release']

                else:
                    logging.warning('%s: %s got none' % (title[k], u))

    wbook.save(execel_path)
    f = open(TMP, 'w')
    f.write(unicode(json.dumps(movies, indent=4, ensure_ascii=False, encoding='utf8')))
    f.close()
    if database_path == None:
        merge([TMP],target_path)    #后者覆盖前者
    else:
        merge([database_path,TMP],target_path)
    logging.info('END LOGGING FROM douban_movie_crawler.py')
    os.remove(TMP)

def write_release_to_column_G(excel_path,json_path):
    book = xlrd.open_workbook(excel_path)
    wbook = copy(book)
    movies = json.load(file(json_path))
    titles_in_json = [m['title'] for m in movies.values()]
    for i,sheet in enumerate(book.sheets()):
        titles = sheet.col_values(5)
        wsheet = wbook.get_sheet(i)
        for j, t in enumerate(titles):
            if t in titles_in_json:
                pos = titles_in_json.index(t)
            else:
                print t,"not in json"
                continue
            wsheet.write(j,6,movies.values()[pos]['release'])
    wbook.save(excel_path)


# 把从excel中读取出来的日期转换成 YYYY-mm-dd格式
__s_date = datetime.date (1899, 12, 31).toordinal() - 1
def excel_date_to_date(date):

    if isinstance(date,str):
        date = date.strip()
        if date == '':
            return ''
    if isinstance(date, float):
        date = int(date)
    d = datetime.date .fromordinal(__s_date + date)
    return d.strftime("%Y-%m-%d")


# unit: 10,000
def currency_to_number(currency):
    unit = ''
    number = ''
    for i in currency:
        if str(i).isdigit() or str(i) == '.':
            number += str(i)
        else:
            unit = str(currency)[len(number):]
    money = float(number)
    if unit.strip() == u'亿':
        money = money * 10000
    return money
# 把excel中人工纠正的中国首映日期补充到json文件中去
# 同时删除误爬的电影
def add_release_date(excel_path,json_path):
    movies = json.load(file(json_path))
    book = xlrd.open_workbook(excel_path)

    titles = []
    dates = []
    boxoffice = []
    for sheet in book.sheets():
        t = sheet.col_values(5)
        d = sheet.col_values(6)
        t = [tt.strip() for tt in t]
        d = [excel_date_to_date(dd) for dd in d]
        b = sheet.col_values(1)
        b = [currency_to_number(c) for c in b]
        titles.extend(t)
        dates.extend(d)
        boxoffice.extend(b)

    name_date = dict(zip(titles,dates))
    name_boxoffice = dict(zip(titles,boxoffice))
    for k,m in movies.items():
        if m['title'] not in titles:
            del movies[k]
        if m['title'] not in name_date:
            print m['title']
        if name_date[m['title']] != "":
            m['release'] = name_date[m['title']]
        # if 'release' not in m or m['release'] == None or m['release'] == "":
        #     if m['title'] in titles:
        #         m['release'] = name_date[m['title']]
        if m['title'] in name_boxoffice:
             m['boxoffice'] = name_boxoffice[m['title']]
        else:
            print m['title'],'may be wrong'
    sum = {}
    for m in movies.values():
        year = extract_year(m['release'])
        if year in sum:
            sum[year] += m['boxoffice']
        else:
            sum[year] = m['boxoffice']
    for m in movies.values():
        m['percent'] = m['boxoffice']*1.0/sum[extract_year(m['release'])]
    print sum
    json.dump(movies,file(json_path,'w'),indent=4,ensure_ascii=False)



# movies = get_movies_after_2010(json.load(file('data/douban_movies_6.json')))
# download_by_url('../data/boxoffice_2006_2014.xls', '../data/movies_with_date.json','../data/movies_with_date.json')
# add_release_date('../data/boxoffice_2006_2014.xls','../data/movies_with_date.json')