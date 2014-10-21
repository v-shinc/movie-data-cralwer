#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'chenshini'

import sys

sys.path.append("../BoxOffice")
sys.path.append("../Douban")
sys.path.append('../SinaWeibo')
sys.path.append('../MovieDataThief')
import crawler_58921
import movie_cralwer_with_api
import sina_crawler
import douban_movie_crawler
import youku_crawler
import xlrd
from xlutils.copy import copy
from copy import deepcopy
import xlwt
import os

# 比较两份Excel 1 和 Excel 2, 导出Excel 1不存在或缺失链接的条目 存储为Excel文件
def export_difference(excel1, excel2,excel3):
    rbook1 = xlrd.open_workbook(excel1)
    rbook2 = xlrd.open_workbook(excel2)
    wbook3 = xlwt.Workbook()
    names = rbook1._sheet_names
    wbook1 = copy(rbook1)
    #收集excel1中还未找到链接的电影
    # for sheet in rbook1.sheets():
    #     name = sheet.name
    #     sheet3 = wbook3.add_sheet(name)
    #     nrow3 = 0
    #     ncols1 = sheet.ncols
    #     titles = sheet.col_values(0)
    #     urls = sheet.col_values(4)
    #     for i,v in enumerate(titles):
    #         if urls[i] == '':
    #             for j in range(ncols1):
    #                 sheet3.write(nrow3,j,sheet.cell_value(i,j))
    #             nrow3 += 1

    sheet1_dict = wbook1._Workbook__worksheet_idx_from_name
    sheet1_names = rbook1._sheet_names
    for idx, sheet2 in enumerate(rbook2.sheets()):
        sheet2_name = sheet2.name
        sheet3 = wbook3.add_sheet(sheet2_name)
        if sheet2_name not in sheet1_names:
            cols = sheet2.ncols
            rows = sheet2.nrows
            for i in range(rows):
                for j in range(cols):
                    sheet3.write(i,j,sheet2.cell_value(i,j))
        else:
            sheet1 = rbook1.sheet_by_name(sheet2_name)
            wsheet1 = wbook1.get_sheet(sheet1_dict[sheet2_name])
            titles_in_1 = sheet1.col_values(0)
            titles_in_2 = sheet2.col_values(0)
            cols = sheet1.ncols
            last_row_of_sheet3 = 0
            for i,title2 in enumerate(titles_in_2):
                if title2 in titles_in_1:
                    #更新原来的票房
                    pos = titles_in_1.index(title2)
                    for j in range(min(4,cols)):
                        wsheet1.write(pos,j,sheet2.cell_value(i,j))
                else:

                    for j in range(sheet2.ncols):
                        sheet3.write(last_row_of_sheet3,j,sheet2.cell_value(i,j))
                    last_row_of_sheet3 += 1

    wbook1.save(excel1)
    wbook3.save(excel3)

def export_union(database_path,difference_path):
    rbook1 = xlrd.open_workbook(database_path)
    wbook1 = copy(rbook1)
    rbook2 = xlrd.open_workbook(difference_path)
    names1 = rbook1._sheet_names
    sheet2_dict = wbook1._Workbook__worksheet_idx_from_name

    for sheet in rbook2.sheets():
        name = sheet.name
        if name in names1:
            rsheet1 = rbook1.sheet_by_name(name)
            wsheet1 = wbook1.get_sheet(sheet2_dict[name])
            titles1 = rsheet1.col_values(0)
            titles2 = sheet.col_values(0)
            last_row = rsheet1.nrows
            for i,t in enumerate(titles2):
                if t in titles1:
                    idx = titles1.index(t)
                    if sheet.ncols > 4:
                        wsheet1.write(idx,4,sheet.cell_value(i,4))
                else:
                    cols = sheet.ncols
                    for j in range(cols):
                        wsheet1.write(last_row,j,sheet.cell_value(i,j))
                    last_row += 1
        else:
            wsheet1 = wbook1.add_sheet(name)
            _nrows =  sheet.nrows
            for i in range(_nrows):
                for j in range(5):
                    print sheet.cell_value(i,j)
                    wsheet1.write(i,j,sheet.cell_value(i,j))
    wbook1.save(database_path)

def add_flag(excel_path,col_index,flag):
    rbook = xlrd.open_workbook(excel_path)
    wbook = copy(rbook)

    for idx,rsheet in enumerate(rbook.sheets()):
        wsheet = wbook.get_sheet(idx)
        for i in range(rsheet.nrows):
            wsheet.write(i,col_index,flag)
    wbook.save(excel_path)

#Excel 格式： A电影名称 B票房 C场次 D人数 E豆瓣链接 F豆瓣中的电影名 G上映日期 H微博相关数 I优酷链接
START_YEAR = 2014
END_YEAR = 2015
NEW_BOX_OFFICE_EXCEL_PATH = '../data/boxoffice2014.xls'
BOX_OFFICE_EXCEL_DATABASE_PATH = '../data/boxoffice_2006_2014.xls'
MOVIE_DATABASE_PATH = '../data/movies_with_date.json'
DIFFERENCE_EXCEL_PATH ='../data/difference.xls'
#下载最新票房数据
print 'Download the lastest box office.'
crawler_58921.download_boxoffice_as_excel(START_YEAR, END_YEAR, NEW_BOX_OFFICE_EXCEL_PATH) # [start,end)
#更新票房数据并且导出之前不存在的电影
print 'Export difference.xls.'
export_difference(BOX_OFFICE_EXCEL_DATABASE_PATH,NEW_BOX_OFFICE_EXCEL_PATH,DIFFERENCE_EXCEL_PATH)
#根据difference.xls中的电影名，用豆瓣API获得豆瓣链接
print 'Get douban url.'
movie_cralwer_with_api.collect_movie_url(DIFFERENCE_EXCEL_PATH)
is_continue = raw_input("Please check the douban url in difference.xls.")
if is_continue == 'y':
    #第H列标记是否要从豆瓣获取元数据
    add_flag(DIFFERENCE_EXCEL_PATH,7,-1)
    #从豆瓣爬取元数据
    douban_movie_crawler.download_by_url(DIFFERENCE_EXCEL_PATH,MOVIE_DATABASE_PATH,MOVIE_DATABASE_PATH)
    #把豆瓣上映日期记录在G列
    douban_movie_crawler.write_release_to_column_G(DIFFERENCE_EXCEL_PATH,MOVIE_DATABASE_PATH)
    #人工确认日期
    is_continue = raw_input('Please check release date (column G) in difference.xls')
    if is_continue == 'y':
        #此处第H列标记为-1表示需要获取weibo_search
        add_flag(DIFFERENCE_EXCEL_PATH,7,-1)
        #获取上映前7日内微博相关数
        sina_crawler.get_weibo_index(DIFFERENCE_EXCEL_PATH)
        #手工添加优酷链接
        has_added = raw_input('please add youku url')
        if has_added == 'y':
            # 更新数据库中的优酷指数
            youku_crawler.get_youku_index_by_excel(DIFFERENCE_EXCEL_PATH,8)
        export_union(BOX_OFFICE_EXCEL_DATABASE_PATH,DIFFERENCE_EXCEL_PATH)


# os.remove(DIFFERENCE_EXCEL_PATH)
os.remove(NEW_BOX_OFFICE_EXCEL_PATH)

# movie_cralwer_with_api.collect_movie_url(BOX_OFFICE_EXCEL_DATABASE_PATH)

