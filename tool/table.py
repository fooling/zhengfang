#-*- coding:utf-8 -*-


from BeautifulSoup import BeautifulSoup as BS

import os
import re
from collections import defaultdict
from MySQLdb

class Table(object):
    

    row_parse={ 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7, 9:8, 10:9, 11:10, 12:11, 13:12 }
    col_parse={ 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7 }

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
                data=col.renderContents()
                while row_i in matrix and col_i in matrix[row_i]:
                    col_i+=1
                for i in xrange(row_i,row_i+rowspan):
                    for j in xrange(col_i,col_i+colspan):
                        matrix[i][j]=data


        self.__matrix=matrix


    def travel(self):
        for i in self.__matrix:
            print i
                
            

    def look(self,x,y):
        
        self.__parse_grid(self.__matrix[x][y],x,y) 

    def all_grid(self):
        for i in self.row_parse:
            for j in self.col_parse:
                self.__parse_grid(self.__matrix[i][j],i,j)

    
    def __parse_grid(self,grid,row,col):
        week=self.col_parse[col]
        seq=self.row_parse[row]
        classes=[]
        
        
        if grid=="&nbsp;":
            print "Nothing"
            return 
            
        for oneclass in grid.split("<br /><br /><br />"):
            print "\n"
            try:
                one={}
                classinfo=oneclass.split("<br />")
                one['name']=classinfo[0]
                tmptime=classinfo[1]
                one['teacher']=classinfo[2]
                one['room']=classinfo[3]
                one['timeinfo']=self.__parse_time(tmptime)
                classes.append(one)
            except:
                pass

        print week,seq
        print classes
            

    def __parse_time(self,timeinfo):
        _time={}
        freqs={
            '周':1,
            '双周':2,
            '单周':3
        }
        _time['num']=timeinfo.split("节")[0]
        tmpfreq=timeinfo.split("/")[1].split('(')[0]
        _time['freq']=freqs.get(tmpfreq,1)
        _time['period']=timeinfo.split('(')[1].split(')')[0].split('-')
        for i,j in enumerate(_time['period']):
            _time['period'][i]=int(j)
        return _time
            




def get_all():
    for f in os.listdir("tables"):
        with open ('tables/'+f) as tmp:
            print f
            data=tmp.read()
        yield data




tmp=''
time=6
gen=iter(get_all())
for i in xrange(time):
    tmp=gen.next()


t=Table(tmp)

t.run()

while True:
    pair=raw_input("input > ")
    x,y= pair.split(' ')
    x=int(x)
    y=int(y)
    print x,y
    t.all_grid()
    t.look(x,y)
    
