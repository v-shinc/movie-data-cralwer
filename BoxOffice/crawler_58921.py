#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'

import urllib
import urllib2
import cookielib
import re
from bs4 import BeautifulSoup
import xlwt
import os
# url = 'http://58921.com/alltime/2014'
def get_website(year, page):
    data = None
    try:
        url = 'http://58921.com/alltime/{0}?page={1}'.format(year,page)
        print url
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        data = res.read()
        # print data
    except urllib2.URLError:
        print url, "=>", "an error occurs"
        # data = ""
    finally:
        return data


def extract_boxoffice(html):

    soup = BeautifulSoup(html)
    trs = soup.select("div .table-responsive > table > tbody tr")
    pt = re.compile(r'<a href="/film/[0-9]+" title="[^"]+">(?P<title>[^>]+)</a></td><td>(?P<boxoffice>[^<]+)</td><td>(?P<audience>[^<]+)</td><td>(?P<screening>[^<]+)</td>')
    t = []
    a = []
    s = []
    b = []
    for tr in trs:
        res = pt.search(str(tr))
        title = res.group('title')
        boxoffice = res.group('boxoffice')
        audience = res.group('audience')
        screen = res.group('screening')
        t.append(title)
        b.append(boxoffice)
        a.append(audience)
        s.append(screen)
        print title,boxoffice,audience,screen
    return t, b, a, s
    print res.read()

def has_next_page(html):
    return not re.search('下页',html) == None

def collect_boxoffice_by_year(year):

    html = get_website(year,0)
    soup = BeautifulSoup(html)
    # page_count = len(soup.select('.pager > .pager_item'))
    titles, boxoffices, audiences, screens = extract_boxoffice(html)
    t = []
    a = []
    s = []
    b = []
    t.extend(titles)
    a.extend(audiences)
    s.extend(screens)
    b.extend(boxoffices)
    i = 1
    while has_next_page(html):
        html = get_website(year,i)
        titles, boxoffices, audiences, screens = extract_boxoffice(html)
        t.extend(titles)
        a.extend(audiences)
        s.extend(screens)
        b.extend(boxoffices)
        i += 1
    return t, b, a, s

def login():
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    print "[step1] to get cookie 58921"
    main_url = "http://58921.com/"
    maib_res = urllib2.urlopen(main_url) # get cookie
    # for index, cookie in enumerate(cj):
    #     print '[',index, ']',cookie
    get_token_Url="http://58921.com/user/login"
    get_token_res=urllib2.urlopen(get_token_Url)

    p = re.compile('<input type="hidden" name="form_token" value="(?P<token>[0-9a-zA-Z]+)"\/>')
    token = p.search(get_token_res.read()).group('token')
    logi_url = "http://58921.com/user/login/ajax?ajax=submit&__q=user/login"
    post = {
        'mail':'1542168876@qq.com',
        'pass':'Woshi456',
        'form_id':'user_login_form',
        'form_token':token,
        'submit': '登录',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:30.0) Gecko/20100101 Firefox/30.0',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    }
    req = urllib2.Request(logi_url, urllib.urlencode(post),headers)
    res = urllib2.urlopen(req)

def download_boxoffice_as_excel(start_year,end_year, export_path):
    login()
    book = xlwt.Workbook(encoding="utf-8")
    for i in range(end_year-1,start_year-1,-1):
        sheet = book.add_sheet(str(i))
        titles, boxoffices, audiences, screens = collect_boxoffice_by_year(i)
        for j in range(len(titles)):
            sheet.write(j,0,titles[j])
            sheet.write(j,1,boxoffices[j])
            sheet.write(j,2,audiences[j])
            sheet.write(j,3,screens[j])
    book.save(export_path)

# download_boxoffice_as_excel(2004,2014,'../data/boxoffice_2005_2014.xls')

#从58921.com下载每一年的电影总票房
# 输入为 开始年份 结束年份 导出的excel路径
# excel 中，每一年为一个sheet，sheet按年份命名