#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'
# merge box-office, baidu index into movies' meta data
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("MovieDataThief")
import xlrd
import xlwt
from xlutils.copy import copy
import MovieDataThiefDB
import datetime
def merge(inputs,output):
    movies = {}
    for i in inputs:
        m = json.load(file(i))
        for k,v in m.items():
            movies[k] = v

    f = open(output,'w')
    f.write(json.dumps(movies,indent= 4,ensure_ascii= False))
    f.close()

def add_release_date_to_excel(excel_path,movies):
    rbook = xlrd.open_workbook(excel_path)
    rsheet = rbook.sheet_by_index(0)
    wbook = copy(rbook)
    wsheet = wbook.get_sheet(0)
    titles = rsheet.col_values(0)
    for i in range(len(titles)):
        t = titles[i]
        for m in movies.values():
            if m['title'] == t:
                wsheet.write(i, 5, m['release'])
                break
    wbook.save(excel_path)


#TODO: 改成读取多sheet
def merge_boxoffice_from_excel(excel_path,movies):
    excel = xlrd.open_workbook(excel_path)


    table = excel.sheets()[0]
    title = table.col_values(0)
    boxoffice = table.col_values(1)
    size = len(title)
    title_in_json = [m['title'] for m in movies.values()]
    for i in range(size):
        if title[i] in title_in_json:
            for m in movies.values():
                if m['title'] == title[i]:
                    m['boxoffice'] = boxoffice[i]
                    break
        else:
            print "xxxx",title[i]
    return movies
    # f = open(output,'w')
    # f.write(json.dumps(movies,indent= 4,ensure_ascii= False))
    # f.close()

def merge_baidu_index_from_excel(excel_path,movies):
    excel = xlrd.open_workbook(excel_path)
    table =  excel.sheets()[0]
    titles = table.col_values(0)
    for i in range(len(titles)):
        t = titles[i]
        for m in movies.values():
            if t == m['title']:
                sum = 0
                for k in range(2,9):
                    sum += int(table.cell_value(i,k))
                sum = sum*1.0/7
                m['baidu_index'] = sum
    return movies
def merge_weibo_search_num_from_excel(excel_path,movies):
    book = xlrd.open_workbook(excel_path)
    for sheet in book.sheets():
        titles = sheet.col_values(0)
        search_num = sheet.col_values(6)
        titles_in_json = [m['title'] for m in movies.values()]
        for idx,title in enumerate(titles):
            if title not in titles_in_json:
                continue
            pos = titles_in_json.index(title)
            m = movies.values()[pos]
            if (search_num[idx] == '' or int(search_num[idx]) == -1):
                if 'weibo_search' in m:
                    del m['weibo_search']
            else:
                m['weibo_search'] = int(search_num[idx])
    return movies


def special(key,movies):
    sum_a = 0
    cnt_a = 0
    # sum_d = 0
    # cnt_d = 0
    for m in movies.values():
        if 'boxoffice' in m:
            sum_a += len(m[key])*currency_to_number(m['boxoffice'])
            cnt_a += len(m[key])
    return sum_a*1.0/cnt_a

def filter(old):
    movies = {}
    for k,v in old.items():
        if 'boxoffice' not in v or 'weibo_search' not in v or v['weibo_search'] == -1:
            continue
        movies[k] = v
    return movies

def clear_date(movies):
    for m in movies.values():
        if 'weibo_search' in m:
            m['weibo_search'] = -1
        if 'boxoffice' in m:
            del m['boxoffice']

def skip_by_date_range(date):
    if date >= '2014-01-01':
        return False
    return True

def merge_youku_index_from_db(movies):
    mdt = MovieDataThiefDB.MovieDataThiefDB()
    for m in movies.values():
        t = m['title']
        release = m['release']
        if skip_by_date_range(release):
            continue

        release_date = datetime.datetime.strptime(str(release).strip(), '%Y-%m-%d')
        before7 = (release_date - datetime.timedelta(days = 7)).strftime('%Y-%m-%d')
        before1 = (release_date - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
        res_dict = mdt.get_youku_index_by_date_range(t, before7, before1)
        sum = int(0)

        if res_dict == None:
            continue

        for k,v in res_dict.items():

            sum += int(v)
        sum = sum *1.0 / 7
        m['youku_index'] = sum

    return movies
# douban_data_path 是过滤后的豆瓣电影文件 2014年电影 top3演员 top1导演
def merge_main(baidu_index_path,box_office_path,douban_data_path):

    movies = json.load(file(douban_data_path))
    # clear_date(movies)
    # movies = merge_boxoffice_from_excel(box_office_path,movies)
    movies = merge_weibo_search_num_from_excel(box_office_path,movies)
    movies = filter(movies)
    movies = merge_baidu_index_from_excel(baidu_index_path,movies)
    # movies = people_box_office('actors',movies)
    # movies = people_box_office('directors',movies)
    movies = merge_youku_index_from_db(movies)
    f = open(douban_data_path,'w')
    f.write(json.dumps(movies,indent= 4,ensure_ascii= False))
    f.close()

# unit: 10,000
def currency_to_number(currency):
    # print currency
    if isinstance(currency,float) or isinstance(currency,int):
        return currency
    unit = ''
    number = ''
    for i in currency:
        if str(i).isdigit() or str(i) == '.':
            number += str(i)
        else:
            unit = str(currency)[len(number):]
    money = float(number)
    if unit == u'亿':
        money = money * 10000
    elif unit == u'万':
        pass
    # print money
    return money

def satisfy_export_condition(movie):
    if movie['release'] < '2014-01-01':
        return False
    if 'boxoffice' not in movie or movie['boxoffice'] == '':
        return False
    if 'baidu_index' not in movie:
        return False
    if 'actors_box_office' not in movie:
        return False
    if 'directors_box_office' not in movie:
        return False
    return True
def export_excel(movies,excel_path):
    book = xlwt.Workbook(encoding="utf-8")
    sheet1 = book.add_sheet('metadata')
    # excel = xlrd.open_workbook('actors.xls')
    # table = excel.sheets()[0]
    sheet1.write(0,0,'电影')
    sheet1.write(0,1,'想看')
    sheet1.write(0,2,'百度指数')
    sheet1.write(0,3,'演员历史票房')
    sheet1.write(0,4,'导演历史票房')
    sheet1.write(0,5,'微博搜索')
    sheet1.write(0,6,'上映时间')
    sheet1.write(0,7,'优酷指数')
    sheet1.write(0,8,'总票房')
    idx = 1
    #TODO: only export the movie which has box-office
    for m in movies.values():
        if not satisfy_export_condition(m):
            continue
        sheet1.write(idx,0,m['title'])
        sheet1.write(idx,1,int(m['wishes']))
        sheet1.write(idx,2,m['baidu_index'])
        #动画片没有演员导演历史票房
        if 'actors_box_office' in m:
            sheet1.write(idx,3,m['actors_box_office']*1000000)
        if 'directors_box_office' in m:
            sheet1.write(idx,4,m['directors_box_office']*1000000)

        sheet1.write(idx,5,m['weibo_search'])
        sheet1.write(idx,6,m['release'])
        sheet1.write(idx,7,m['youku_index'])
        sheet1.write(idx,8,m['boxoffice'])
        idx += 1

    book.save(excel_path)
    f = open('data/final.txt','w')
    idx = 1
    for m in movies.values():
        if not satisfy_export_condition(m):
            continue
        if 'boxoffice' not in m or 'baidu_index' not in m:
            continue
        f.write('{0} {1} {2} {3} {4} {5} \n'.format(int(m['wishes']), int(m['baidu_index']), int(m['actors_box_office']*1000000),int(m['weibo_search']),int(m['youku_index']),int(m['boxoffice'])))
    f.close()


#TODO: 1.baidu_index 2. directors' box-office 3.actors' box-office 4.like 5. is serial
# merge_main("data/baidu_index.xlsx",'data/boxoffice.xls','data/res.json')
export_excel(json.load(file('data/res.json')),'data/final.xls')

# add_release_date_to_excel('data/boxoffice.xls',json.load(file('data/douban_movies_0723.json')))

