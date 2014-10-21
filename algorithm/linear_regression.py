#!/usr/bin/env python
# -*- coding : utf-8 -*-
__author__ = 'DELL'

import xlrd
from sklearn import linear_model
from sklearn import cross_validation
import  numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def read_input(excel_path):
    book = xlrd.open_workbook(excel_path)
    table = book.sheet_by_index(0)

    nrow = table.nrows
    movies = []
    boxoffice = []
    for i in range(1, nrow):
        m = []
        m.extend([table.cell_value(i,2),table.cell_value(i,3), table.cell_value(i,5),table.cell_value(i,7)])
        movies.append(m)
        boxoffice.append(table.cell_value(i,8))
    return movies, boxoffice

def linear_regression(X, Y, ith):
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size=0.23, random_state=2)
    print 'X test\'s shape', X_test.shape

    # num = 8
    # PX = X[ith*num:ith*num+num]
    # TARGET = Y[ith*num:ith*num+num]
    # TX = []
    # TY = []
    # for i in range(0,ith*num):
    #     TX.append(X[i])
    # for i in range(ith*num+num,):
    #     TX.append(X[i])
    #
    # for i in range(0,ith*num):
    #     TY.append(Y[i])
    # for i in range(ith*num+num,):
    #     TY.append(Y[i])
    # print(X[:ith*num])
    # print(X[num*ith+num:])
    # TX = X[:ith*num].extend(X[num*ith+num:])
    # TY = Y[:ith*num].extend(Y[num*ith+num:])
    # extend(Y[num*ith+num:])


    clf = linear_model.Lasso(alpha = 1)
    clf.fit(X_train, y_train)
    # scores = cross_validation.cross_val_score(clf, X, Y)
    # print scores
    print(clf.coef_)
    y_predict = clf.predict(X_test)
    # The mean square error
    print("Residual sum of squares: %.2f"
          % np.mean((y_predict - y_test) ** 2))
    print('Variance score: %.2f' % clf.score(X_test, y_test))
    sum = 0
    for i in range(len(y_predict)):
        if y_predict[i]*1.0/y_test[i]>0.5 and y_predict[i]*1.0/y_test[i]<1.5:
            sum += 1
        print y_predict[i]*1.0/y_test[i]
    return (sum*1.0/len(y_predict))

def cross_fold(X,Y):
    sum = 0.0
    for i in range(10):
        sum += linear_regression(X,Y,i)
    print 'result:',sum/10
# linear_regression(read_input('newFinal.xls'),0)
X,Y = read_input('../data/final.xls')
cross_fold(X,Y)

