#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'


# order data by year
# only remain movies that released after 2010
# extend actor to historical box-office, number of search within a certain period, weibo followers (top3)
import re
import json
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# 预处理数据 只取2014年的数据 保留top3演员 top1导演
def extract_year(date):

    p = re.compile(r'[0-9]{4}')
    y = p.match(date)
    if not y == None:
        return y.group()
    return 0

def is_normalize_date(date):
    p = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')
    if p.match(date) == None:
        return False
    return True

def get_movies_after_2014(m2014,movies):
    # movies = json.dump(file(input))

    for k,v  in movies.items():
        if is_normalize_date(v['release']) == False:
            continue
        y = extract_year(v['release'])
        if int(y) >= 2014:
            # print '>2010',y
            m2014[k] = v
            print v['title']
            m2014[k]['year'] = y
    return m2014
def top3_actors(movies):
    for m in movies.values():
        end = min(3,len(m['actors']))
        m['actors'] =  m['actors'][:end]
    return movies

def top1_director(movies):
    for m in movies.values():
        # end = min(3,len(m['director']))
        m['directors'] = m['directors'][:1]
    return movies


def filter_and_merge(inputs,output):
    m2014 = {}
    for i in inputs:
        m2010 = get_movies_after_2014(m2014, json.load(file(i)))

    m2014 = top3_actors(m2014)
    m2014 = top1_director(m2014)
    f = open(output,'w')
    f.write(json.dumps(m2014,indent= 4,ensure_ascii= False))
    f.close()



filter_and_merge(['data/douban_movies_m.json'],'data/douban_movies_2014.json')
