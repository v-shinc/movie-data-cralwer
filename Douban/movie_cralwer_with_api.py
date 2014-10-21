#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'

import urllib2
import urllib
import json
import xlrd
import xlwt
import re
from xlutils.copy import copy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
API_KEY0 = '023aa6edb1c29e9806aff4c91547dbc8'
API_KEY1 = '0d0aaf328d09e64827200d97a71db2d8'
API_KEY2 = '064629a2fa951de112d27ce8efbf59a3'
# http://api.douban.com/v2/movie/subject/:id?apikey=XXX, XXX
def request_data_by_api(url):
    # search_url = 'http://api.douban.com/v2/movie/search?q={0}&apikey={1}'.format(urllib.quote(title),API_KEY)
    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        return res.read()
    except:
        print url ,'=> error'
        return None

def extract_movie_meta_data(raw_data):
    data = json.loads(raw_data)
    # print json.dumps(data, sort_keys=True,indent=4, separators=(',', ': '))
    if data['subtype'] != 'movie':
        return None

    movie = {}
    movie['aka'] = data['aka']
    movie['alt'] = data['alt']
    movie['casts'] = [{'name':c['name'],'alt':c['alt']} for c in data['casts']]
    movie['directors'] = [{'name':c['name'],'alt':c['alt']} for c in data['directors']]
    movie['collect_count'] = data['collect_count']
    movie['countries'] = data['countries']
    movie['genres'] = data['genres']
    movie['title'] = data['title']
    movie['wish_count'] = data['wish_count']
    if 'mainland_pubdate' in data:
        movie['release'] = data['mainland_pubdate']
    if 'release' not in movie and 'release' in data:
        movie['release'] = data['pubdate']
    return movie
def download_meta_data(url_path,export_path,database_path = None):
    rbook = xlrd.open_workbook(url_path)
    # wbook = xlwt.Workbook(export_path)
    if database_path == None:
        movies = {}
    else:
        movies = json.load(file(database_path))
    for sheet in rbook.sheets()[1:4]:
        year = sheet.name
        # wsheet = wbook.add_sheet(year,cell_overwrite_ok=True)
        for i in range(sheet.nrows):
            if sheet.cell_value(i,4) != '':
                m = re.search('[0-9]+',sheet.cell_value(i,4))
                id = m.group()
                print m.group()
                url = 'http://api.douban.com/v2/movie/subject/{0}?apikey={1}'.format(id,API_KEY0)
                data = request_data_by_api(url)
                movie = extract_movie_meta_data(data)
                movies[id] = movie
    f = open(export_path, 'w')
    f.write(unicode(json.dumps(movies, indent=4, ensure_ascii=False, encoding='utf8')))
    f.close()
    # json.dump(movies,file(export_path),indent=4)

# extract_movie_meta_data(request_data_by_api('后会无期'))
# download_meta_data('../data/boxoffice_2005_2014.xls','../data/movies_2009_2005.json')
def extract_alt(data,year):
    if data == None:
        return None
    for s in json.loads(data)['subjects']:
        if s['subtype'] == 'movie': #and s['year'] == year:
            return s['alt']
    return None
url = 'http://api.douban.com/v2/movie/subject/{0}?apikey={1}'.format('25805741',API_KEY1)
def collect_movie_url(excel_path):
    rbook = xlrd.open_workbook(excel_path)
    wbook = copy(rbook)
    j =0
    for sheet in rbook.sheets():
        year = sheet.name
        ncols = sheet.ncols
        wsheet = wbook.get_sheet(j)
        j += 1
        for i in range(sheet.nrows):
            if sheet.ncols > 4 and sheet.cell_value(i, 4) != '':
                continue
            title = sheet.cell_value(i, 0)
            search_url = 'http://api.douban.com/v2/movie/search?q={0}&apikey={1}'.format(urllib.quote(str(title)),API_KEY2)
            data = request_data_by_api(search_url)
            alt = extract_alt(data,year)
            wsheet.write(i,4,alt)
            wsheet.write(i,5,title)
            print alt
    wbook.save(excel_path)
# collect_movie_url('../data/boxoffice_2005_2014.xls')