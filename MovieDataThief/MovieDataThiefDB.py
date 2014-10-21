#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
from pymongo import Connection
from pymongo.errors import ConnectionFailure

class MovieDataThiefDB():

    connection = None
    dbh = None
    def __init__(self):
        try:
            connection = Connection(host = "localhost",port=27017)
            self.dbh = connection['MovieThiefDB']

        except ConnectionFailure, e:
            sys.stderr.write('Could not connect to MongoDB: %s' % e)
            sys.exit(1)
    def insert_youku_index(self, name, date, value):
         # self.dbh.youku_index.create_index('youku_index.date',unique=True)
         self.dbh.youku_index.update({'title':name},
                                    {'$set':{"youku_index."+date:value}},
                                    upsert=True,
                                    safe=True)
    # def insert_youku_index(self,name,date):

    def delete_youku_index(self,name,date):
        self.dbh.youku_index.update({'title':name},{'$unset':{"youku_index."+date:1}},safe = True)

    def get_youku_index_by_name_and_date(self,name,date):
        movie_doc = self.dbh.youku_index.find_one({'title':name,'youku_index.'+date:{'$exists':True}},safe = True)

        if not movie_doc:
            print 'find no result'
            return None
        else:
            # print date,movie_doc['youku_index'][date]
            return movie_doc
    def get_all_youku_index_by_name(self):
        pass
    def get_youku_index_by_date_range(self,name,start,end):
        end_date = datetime.datetime.strptime(str(end).strip(), '%Y-%m-%d')
        current_date = datetime.datetime.strptime(str(start).strip(), '%Y-%m-%d')
        fields ={}
        while current_date <= end_date:
            current = current_date.strftime('%Y-%m-%d')
            fields['youku_index.'+current] = 1
            current_date = current_date + datetime.timedelta(days = 1)
        fields['_id'] = 0
        # print fields
        res = self.dbh.youku_index.find({'title':name},fields)
        b= {}
        for r in res:
            for k,v in r['youku_index'].items():
                if 'youku_index.'+k in fields.keys():
                    b[k] = v
            return b

            # return [a for a in r if a in fields]
    def get_all_you_index_by_date(self):
        pass
# print MovieDataThiefDB().get_youku_index_by_date_range('美国队长2','2014-06-01','2014-06-07')