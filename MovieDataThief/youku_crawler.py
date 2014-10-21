#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'

import re
from bs4 import BeautifulSoup
import json
import urllib
import urllib2
import datetime
import xlrd
import MovieDataThiefDB
from MovieDataThiefDB import  MovieDataThiefDB
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def get_website(url):
    data = None
    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        data = res.read()
        # print data
    except urllib2.URLError:
        print url, "=>", "an error occurs"
        # data = ""
    finally:
        return data
def search_youku(title):
    data = None
    parameters = {
        'f': 1,
        'kb': '0212000000000_变形金刚4:绝迹重生(2014)预告片_变形金刚4:绝迹重生 预告片'
    }
    # title = '爸爸去哪儿 电影 预告片'
    url = "http://www.soku.com/search_video/q_{0}?{1}".format(urllib.quote(title), urllib.urlencode(parameters))
    # print url
    try:
        # cookie = cookielib.CookieJar()
        # cookie_handler = urllib2.HTTPCookieProcessor(cookie)
        #
        # heads = {'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'}
        # req = urllib2.Request(url, heads = heads)
        # opener = urllib2.build_opener(cookie_handler)
        # res = opener.open(req)
        # data = res.read()

        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        data = res.read()
        # print data
    except urllib2.URLError:
        print url, "=>", "an error occurs"
        # data = ""
    finally:
        return data


def parse_html(html):
    """

    :param html: string
    """
    if html == "" or html == None:
        return -1
    soup = BeautifulSoup(html)
    tags = soup.select("div .DIR > div:nth-of-type(1) > .movie  .play > .num")
    if len(tags) == 0:
        return -1
    play_num_tag = str(tags[0])
    p = re.compile(r'<b>(?P<num>[0-9.]+)<\/b>')
    play_num = p.search(play_num_tag).group('num')
    if re.search("万", play_num_tag) != None:
        play_num = float(play_num) * 10000
    print float(play_num)
def extract_youku_index_url(html):
    if html == "" or html == None:
        return -1
    soup = BeautifulSoup(html)
    tags = soup.select("div .DIR > div:nth-of-type(1) > .movie  .play > .num > a")

    if len(tags) == 0:
        return -1
    play_num_tag = str(tags[0])
    p = re.compile(r'<a href=\"(?P<url>[^\"]+)\"')
    res = p.search(play_num_tag)
    if res != None:
        # print res.group('url')
        return res.group('url')
    else:
        print 'Find no you index url'
        return None

def feed_titles(titles):
    nums = []
    for t in titles:
        html = get_website(titles+' 预告片')
        play_num = parse_html(html)
        nums.append(play_num)
    return nums

def add_youku_trailer_play_num(json_path):
    movies = json.load(file(json_path))

# parse_html(get_website())

def request_youku_index_page(index_url):
    page = None
    try:
        req = urllib2.Request(index_url)
        res = urllib2.urlopen(req)
        page = res.read()

    except:
        print index_url, "=>", "an error occurs"
    finally:
        return page
# def extract_youku_config(html):{
#     p = re.compile(r'var youkuconfig = \{[ ]*groups[ ]:[ ]\[\{\'key\': \'vv\', \'value\': \'播放\'\}\][ ]*\}')
def extract_youku_index_date(html):
    if html == None:
        print 'extract youku_index data => html is none'
        return None

    p = re.compile(r'var youkuData = eval\(\'\(\'[+](?P<youkuData>[^+]+)\+\'\)\'\)')
    res = p.search(html)
    start = ""
    end = ""
    data = []
    if res != None:
        # print str(res.group('youkuData'))[2:-2]

        youku_data = json.loads(str(res.group('youkuData'))[2:-2])
        movie_title = youku_data['name']
        vv = youku_data['vv']
        start = vv[1]
        end = vv[0]
        data = vv[2]
        # print start,end
        map = map_date_to_data(start,end,data)
        # print map
        # print map['2014-07-15']
        return map
    else:
        print "Find no youku data!"
        return None
# data 是反序的
def map_date_to_data(start,end,data):
    youku_index = {}
    end_date = datetime.datetime.strptime(str(end).strip(), '%Y-%m-%d')
    current_date = datetime.datetime.strptime(str(start).strip(), '%Y-%m-%d')
    # print len(data)
    if (end_date - current_date).days == len(data):
        current_date += datetime.timedelta(days=1)
    while current_date <= end_date and len(data)>0:
        current = current_date.strftime('%Y-%m-%d')
        # print current
        youku_index[current] = data.pop()
        current_date += datetime.timedelta(days=1)

    return youku_index

# page = request_youku_index_page(r'http://index.youku.com/vr_show/showid_z9f015586984711e3a705?type=youku')
# parse_youku_index_page(page)
#
def get_youku_index_by_title(title):
    mdt = MovieDataThiefDB()
    html = search_youku(title)
    youku_index_url = extract_youku_index_url(html)
    html2 = get_website(youku_index_url)
    date_data = extract_youku_index_date(html2) # {date:data}
    # print date_data
    for date,data in sorted(date_data.items()):
        mdt.insert_youku_index(title,date,data)
    # mdt.get_youku_index_by_date_range(title,'2014-06-06','2014-07-01')

# extract_youku_index_url(get_website('变形金刚4'))
# get_youku_index_by_title('变形金刚4:绝迹重生')

mdt = None

def get_youku_index_by_excel(excel_path,url_col):
    global  mdt
    if mdt == None:
        mdt = MovieDataThiefDB()
    book = xlrd.open_workbook(excel_path)
    for sheet in book.sheets():
        titles = sheet.col_values(0)
        youku_index_urls = sheet.col_values(url_col)
        for idx,url in enumerate(youku_index_urls):
            title = titles[idx]
            html = get_website(url)
            date_data = extract_youku_index_date(html) # {date:data}
            if date_data == None:
                print title ,'=> None'
                continue
            print title
            for date,data in sorted(date_data.items()):
                mdt.insert_youku_index(title,date,data)



get_youku_index_by_excel('../data/difference.xls',8)
# get_youku_index_by_excel('../data/boxoffice.xls')