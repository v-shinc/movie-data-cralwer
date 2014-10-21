#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'

import json
import re
import xlrd
import xlutils
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
def skip_genre_condition(genre):

    # if '动画' in genre:
    #     return True
    # return False
    return False

def build_cast_historical_box_office_dict(identity,movies):
    cast_box_office = {}
    for m in movies.values():
        if skip_genre_condition(m['genre']):
            continue
        casts = m[identity]
        for idx,c in enumerate(casts):
            if c not in cast_box_office:
                cast_box_office[c] = []
            h = {}
            h['title'] = m['title']
            h['percent'] = m['percent']
            h['rank'] = idx
            h['release'] = m['release']
            cast_box_office[c].append(h)
    # for name,history in cast_box_office.items():
    #     print name
    #     for h in history:
    #         print h['title'],h['percent'],h['rank']
    return cast_box_office

def extract_year(date):
    p = re.compile(r'[0-9]{4}')
    y = p.match(date)
    if not y == None:
        return y.group()
    return 0

def skip_year_condition(date):
    y = extract_year(date)
    if y != '2014':
        return True
    else:
        return False

def get_factor(identity,rank):
    if identity == 'directors':
        if rank == 0:
            return 1
        else:
            return 0
    if rank < 3:
        return 0.7
    if rank < 6:
        return 0.3
    return 0

def dete_compare(x,y):
    if y == "":
        return False
    return x > y
def cal_movies_box_office_with_casts(identity,movies, cast_box_office_dict):

    for m in movies.values():
        if skip_year_condition(m['release']) or skip_genre_condition(m['genre']):
            if identity+'_box_office' in m:
                del m[identity+'_box_office']
            continue
        sum = 0
        cnt = 0
        release = m['release']

        for c in m[identity]:
            history = cast_box_office_dict[c]
            for h in history:
                if dete_compare(release,h['release']):
                    cnt += 1
                    sum += h['percent'] * get_factor(identity,h['rank'])
        m[identity+'_box_office'] = sum*1.0/max(cnt,1)
        print m['title'],m['percent'],m[identity+'_box_office']
    return movies


def export_cast_box_office(json_path,export_path):
    movies = json.load(file(json_path))
    cast_box_office_dict = build_cast_historical_box_office_dict('actors',movies)
    movies = cal_movies_box_office_with_casts('actors', movies,cast_box_office_dict)
    director_box_office_dict = build_cast_historical_box_office_dict('directors',movies)
    movies = cal_movies_box_office_with_casts('directors', movies,director_box_office_dict)
    json.dump(movies, file(export_path, 'w'), indent=4, ensure_ascii=False)

export_cast_box_office('../data/movies_with_date.json','../data/res.json')