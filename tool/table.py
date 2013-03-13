#-*- coding:utf-8 -*-


from BeautifulSoup import BeautifulSoup as BS

import os
import re
from collections import defaultdict


class Table(object):
    def __init__(self,table):
        self.__table=table
        pass

    def run(self):
        bs=BS(self.__table)
        matrix=defaultdict(lambda: defaultdict(unicode))
        for row_i,row in enumerate(bs('tr')):
            for col_i,col in enumerate(row('td')):
                rowspan=1
                colspan=1
                try: 
                    rowspan=int(col['rowspan'])
                except:
                    pass
                try:
                    colspan=int(col['colspan'])
                except:
                    pass
                data=col.text
                while row_i in matrix and col_i in matrix[row_i]:
                    col_i+=1
                for i in xrange(row_i,row_i+rowspan):
                    for j in xrange(col_i,col_i+colspan):
                        matrix[i][j]=data


        self.__matrix=matrix


    def travel(self):
        for i in self.__matrix:
            print i
                
    def parse(self):
        for i in self.__matrix




def get_all():
    for f in os.listdir("tables"):
        with open ('tables/'+f) as tmp:
            print f
            data=tmp.read()
        yield data




tmp=''
for data in get_all():
    tmp=data
    break


t=Table(tmp)

t.run()

while True:
    pair=raw_input("input > ")
    x,y= pair.split(' ')
    x=int(x)
    y=int(y)
    print x,y
    t.look(x,y)
    
