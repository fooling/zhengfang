# -*- coding: utf-8 -*-


from BeautifulSoup import BeautifulSoup as BS

import os
import re
from collections import defaultdict
import MySQLdb
import getpass
import json

class Database(object):
    def __init__(self):
        if os.path.exists('config.tmp') is False:
            user= raw_input('database user > ')
            host= raw_input('database host > ')
            passwd=getpass.getpass('database password > ')
            with open('config.tmp','w') as config:
                config.write(json.dumps([user,host,passwd])) 
        else: 
            user,host,passwd=self.__get_ident()

        
        self.__conn=MySQLdb.connect(host=host,user=user,passwd=passwd,charset='utf8')
        self.__conn.select_db('class')
        self.__cursor=self.__conn.cursor()
                
    def __get_ident(self):
        with open('config.tmp') as config:
            return [content for content in json.loads(config.read())]

    def select(self,data,table):
        q="select id,"
        keys=[]
        values=[]
        pairs=[]
        for key,value in data.items():
            key='`%s`' % key
            try:
                value='"%s"' % value
            except:
                try:
                    value='"%d"' % value
                except:
                    pass 
            keys.append(key)
            values.append(value)
            pairs.append(key+'='+value)

        q+=','.join(keys)+' from '+table+' where '+' and '.join(pairs)
        return self.__select_query(q)
        
            
    def insert(self,data,table):
        q="insert into `%s` "% table
        keys=[]
        values=[]
        for key,value in data.items():
            keys.append('`'+key+'`')
            try:
                values.append('"%s"' % value)
            except:
                try:
                    values.append('"%d"' % value )
                except:
                    pass 
        q+='('+','.join(keys)+')'+' values '+'('+','.join(values)+');'
        #with open("tmpquery.sql",'w') as que:
        #    que.write(q)
        return self.__insert_query(q)
        
    def __insert_query(self,q):
        self.__cursor.execute(q)
        self.__conn.commit()
        return self.__cursor.lastrowid
        

    def __select_query(self,q):
        res=self.__cursor.execute(q)
        return self.__cursor.fetchall()


class Table(object):
    

    row_parse={ 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7, 9:8, 10:9, 11:10, 12:11, 13:12 }
    col_parse={ 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7 }

    def __init__(self,table,info):
        self.__table=table
        self.__info=info
        #print info
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
        schedules=[]
        
        
        if grid=="&nbsp;":
            #print "Nothing"
            return 
            
        for oneclass in grid.split("<br /><br /><br />"):
            try:
                one={}
                two={}
                classinfo=oneclass.split("<br />")
                one['name']=classinfo[0]
                tmptime=classinfo[1]
                one['teacher']=classinfo[2]
                timeinfo=self.__parse_time(tmptime)
                one['week_start']=timeinfo['period'][0]
                one['week_end']=timeinfo['period'][1]
                one['num_perweek']=timeinfo['num']

                two['step_type']=timeinfo['freq']
                two['classroom']=classinfo[3]
                classes.append(one)
                schedules.append(two)
            except:
                pass

        for one in classes:
            one['level']=self.__info[0]
            one['year']='2012-2013'
            one['semester']='2'
        db=Database()
        sche_gen=self.__yield_schedule(schedules)
        for i in classes:
            findout=db.select(i,'main')
            if findout==():
                tid=db.insert(i,'main')
            else:
                tid=findout[0][0]

            db.insert({'tid':tid,'idinfo':self.__info[3],'collegeid':self.__info[1],'majorid':self.__info[2],'college':self.__info[4],'major':self.__info[5]},'classes')
            schedule={'tid':tid,'weekday_num':week,'lesson_num':seq}
            schedule.update(sche_gen.next())
            if db.select(schedule,'schedules') ==():
                db.insert(schedule,'schedules')

    def __yield_schedule(self,schedules):
        for schedule in schedules:
            yield schedule
    
    
            


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
            info = f.split('.')[0].split('_')
        yield (data,info)




tmp=''
gen=iter(get_all())
for i in gen:
    tmp,tmpinfo=gen.next()
    t=Table(tmp,tmpinfo)
    t.run()
    t.all_grid()



    
