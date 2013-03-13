#!/usr/bin/env python
#-*- coding=utf-8 -*-


#this core may only work in the period when class-choose is availiable

import re
import os
import urllib
import urllib2
import cookielib
import webbrowser
import random
import time
from BeautifulSoup import BeautifulSoup as BS

class cxcore(object):
    
    xn='2012-2013'
    xq='2'
    __root_host= 'ea.uestc.edu.cn'
    __host_list=[
        '222.197.164.82',
        '222.197.164.244',
        '222.197.165.148',
        '222.197.165.209',
        '222.197.165.74'
    ]
    
    #store viewstates
    __viewstates={}
    #while循环状态
    __state=''
    #当前刷新次数
    __trytime=0
    
    #mode2 选课   mode1  查成绩
    __mode=2

    #class choose


    def __init__(self,username,password):
        if type(username)== type(1):
            username="%d" %username
        self.__username = username
        self.__password = password
        
        for host in self.__host_list:
            self.__viewstates['http://'+host]={}
        stat=self.__login()
        if stat == False:
            print "登陆失败"
            self.__state="down"
            return

        print '登录成功'

    def get_state(self):
        return self.__state

    def __login(self):

        while self.__state=='' and self.__trytime<4000:

            self.__trytime+=1
            print self.__trytime
            self.__login_url=''
            for host in self.__host_list: 
                self.__cookie = cookielib.CookieJar()
                self.__login_data = {'tbYHM':self.__username,'tbPSW':self.__password,'Button1':' 登 录 '}
                root=host
                host='http://'+host
                
                self.__choose_url = host+'/xs_main_zzjk.aspx?xh='+self.__username
                #test connection
                try:
                    response=urllib2.urlopen(host+"/default_ldap.aspx",timeout=1).read().decode("gb2312").encode('utf-8')
                    #print "response",response
                except:
                    continue

                try:
                    tmpViewstate = re.findall('"__VIEWSTATE" value="([^"]+)"',response)[0]
                    self.__viewstates[host].update({time.time():tmpViewstate})
                except:
                    print "exception : no viewstate"
                    continue
                
                self.__login_url=host+'/default_ldap.aspx'
                self.__root_host=root
                #self.__query_url = host+'/default_zzjk.aspx'
                self.__query_url = host+'/xs_main_zzjk.aspx?xh='+self.__username
                print root
                self.__login_header = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Charset':'GBK,utf-8;q=0.7,*;q=0.3','User-Agent':'Mozilla/5.0 (X11;Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.12 Safari/537.31','Content-Type':'application/x-www-form-urlencoded','Connection':'keep-alive'}
                self.__login_header['HOST']=root
                self.__login_header['Referer']=host
                ifstate=self.__getviewstate(host)
                if ifstate == None:
                    print "not viewstate yet"
                    continue
                self.__login_data['__VIEWSTATE']=ifstate
                self.__login_data = urllib.urlencode(self.__login_data)


                tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
                tmpreqhandle = urllib2.Request(self.__login_url,self.__login_data,self.__login_header)
                try:
                    first=tmpopener.open(tmpreqhandle).read().decode('gb2312').encode('utf-8')
                    #print 'first',first
                except:
                    print "login error"
                    continue

                try:
                    self.__tmpcontent = tmpopener.open(self.__query_url).read().decode('gb2312').encode('utf-8')
                except:
                    print "validate error"
                
                
                proof=re.findall("防刷",self.__tmpcontent)
                if proof !=[]:
                    continue
                tmpornot = re.findall('([^\s]+)同学',self.__tmpcontent)
                if tmpornot == []:
                    #print '尚未登陆'
                    continue
                self.__name=tmpornot[0]
                print self.__name
                self.__state='inside'
                return

    

        if self.__login_url=='':
            print "all url down"
            return False

    #login viewstates to avoid 5-seconds-refreash-proof
    def __getviewstate(self,host):
        for age,viewstate in self.__viewstates[host].iteritems():
            if time.time()-age>2:
                return viewstate

        for viewstate in self.__viewstates[host].items():
            return viewstate

        return None

    def __cjcx_query(self,info):
        
        self.__cjcx_data = {'__EVENTTARGET':'','__EVENTARGUMENT':'','hidLanguage':'','ddlXN':'','ddlXQ':'','ddl_kcxz':''}

        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,None,self.__query_header)
        tmpcontent = tmpopener.open(tmpreqhandle,None).read().decode('gb2312').encode('utf-8')

        tmpViewstate = re.search('"__VIEWSTATE" value="([^"]+)"',tmpcontent)
        
        self.__cjcx_data['__VIEWSTATE'] = tmpViewstate.group(1)

        if(info[0] == 2):
            self.__cjcx_data['btn_zcj'] = '历年成绩'
        elif(info[0] == 1):
            self.__cjcx_data['ddlXN'] = info[1]
            self.__cjcx_data['btn_xn'] = '学年成绩'
        elif(info[0] == 0):
            self.__cjcx_data['ddlXN'] = info[1]
            self.__cjcx_data['ddlXQ'] = info[2]
            self.__cjcx_data['btn_xq'] = '学期成绩'
        
        self.__cjcx_data = urllib.urlencode(self.__cjcx_data)

        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,self.__cjcx_data,self.__query_header)
        tmpcontent = tmpopener.open(tmpreqhandle,self.__cjcx_data).read()
        
        self.__save('shit_zf_cjcx_local.html',tmpcontent)

    def __ifcx_query(self,filename):

        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,None,self.__query_header)
        tmpcontent = tmpopener.open(tmpreqhandle,None).read()
        
        self.__save(filename,tmpcontent)


    def crawl_query(self):
        self.__query_header = self.__login_header
        self.__query_header['HOST'] = self.__root_host
        self.__query_header['Referer'] = 'http://'+self.__root_host+'/xs_main_zzjk1.aspx?xh='+self.__username+'&type=1'

        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        self.__tmpcontent=tmpopener.open(self.__query_header['Referer']).read().decode('gb2312').encode('utf-8')

        tmpregurl = re.search('"tjkbcx.aspx\?([^"]+)"',self.__tmpcontent)
        self.__info_url = 'http://'+self.__root_host+'/tjkbcx.aspx?'+tmpregurl.group(1)
        self.__info_url = self.__info_url.decode('utf-8').encode('gb2312')
        self.__tjkbcx()
    
    def __tjkbcx(self):
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,None,self.__query_header)
        tmpcontent = tmpopener.open(tmpreqhandle).read()
        bs=BS(tmpcontent)
        #self.__save("kb.html",unicode(bs).encode('utf-8'),True)
        #return
        #print bs
        njs=[i.text for i in bs("table")[0]("td")[2]("option")][:3] # only look for 3 grades
        self.__table_data={
            '__EVENTTARGET':'nj',
            '__EVENTARGUMENT':'',
            'xn':self.xn,
            'xq':self.xq,
        }
        for nj in njs:
            self.__table_data['nj']=nj
            self.__table_data['xy']='01'
            self.__table_data['zy']='0101'
            self.__table_data['kb']=''
            self.__table_data['__EVENTTARGET']='nj'
            print "开始抓取年级",nj
            self.__tjkbcx_nj(self.__tjkbcx_query(tmpcontent))

    def __tjkbcx_query(self,prevcontent):
        tmpViewstate = re.findall('"__VIEWSTATE" value="([^"]+)"',prevcontent)[0]
        self.__table_data['__VIEWSTATE']=tmpViewstate
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,urllib.urlencode(self.__table_data),self.__query_header)
        tmpcontent = tmpopener.open(tmpreqhandle).read()
        return tmpcontent
        

    def __tjkbcx_nj(self,tmpcontent):
        bs=BS(tmpcontent)

        xys={i['value']:i.text for i in bs("table")[0]("td")[3]("option")}
        for xy in xys:
            self.__table_data['xy']=xy
            self.__table_data['__EVENTTARGET']='xy'
            print "  >>开始抓取学院",xys[xy]
            self.__xy=xys[xy]
            self.__tjkbcx_xy(self.__tjkbcx_query(tmpcontent))
        
            
    def __tjkbcx_xy(self,tmpcontent):
        bs=BS(tmpcontent)
        zys={i['value']:i.text for i in bs("table")[0]('td')[4]('option')}
        for zy in zys:
            self.__table_data['zy']=zy
            self.__table_data['__EVENTTARGET']='zy'
            print "    >>开始抓取专业",zys[zy]
            self.__zy=zys[zy]
            self.__tjkbcx_zy(self.__tjkbcx_query(tmpcontent))
    def __tjkbcx_zy(self,tmpcontent):
        bs=BS(tmpcontent)
        kbs={i['value']:i.text for i in bs("table")[0]('td')[5]('option')}
        for kb in kbs:
            if len(kb) is not 0:
                self.__table_data['kb']=kb
                self.__table_data['__EVENTTARGET']='kb'
                print "      >>开始抓取班级",kbs[kb]
                self.__tjkbcx_kb(self.__tjkbcx_query(tmpcontent))

    def __tjkbcx_kb(self,tmpcontent):
        bs=BS(tmpcontent,fromEncoding="gb18030")
        tmptable=bs('table')[1]
        tablename=self.__table_data['nj']+'_'+self.__table_data['xy']+'_'+self.__table_data['zy']+'_'+self.__table_data['kb']+'_'+self.__xy+'_'+self.__zy+'.html'
        strtable="%s" % tmptable
        self.__save(tablename,strtable,True)
        

        
        

    def __xsxk_query(self,action=0,data=''):
        
        self.__xsxk_data = {
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            'xx':'',
            }

        #print "info_url is \n\n\n",self.__info_url
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,None,self.__query_header)

        tmpcontent = tmpopener.open(tmpreqhandle).read().decode('gb2312').encode('utf-8')
        # for kidding
        while re.findall('防刷',tmpcontent) !=[]:
            tmpcontent = tmpopener.open(tmpreqhandle).read().decode('gb2312').encode('utf-8')

        tmpViewstate = re.search('"__VIEWSTATE" value="([^"]+)"',tmpcontent)
        tmpZymc=re.findall('name="zymc"[^>]+value="([^"]+)',tmpcontent)
        tmpButton5=re.findall('name="Button5" value="([^"]+)',tmpcontent)
        
        self.__xsxk_data['zymc']=tmpZymc[0]
        self.__xsxk_data['__VIEWSTATE'] = tmpViewstate.group(1)
        if action == 1:
            #查看可选课程
            self.__xsxk_data['Button5']=tmpButton5[0]

        
        self.__xsxk_data = urllib.urlencode(self.__xsxk_data)

        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,self.__xsxk_data,self.__query_header)
        if action==1:
            tmpcontent = tmpopener.open(tmpreqhandle).read().decode("gb2312").encode("utf-8")
        if action ==0:
            tmpcontent = tmpopener.open(tmpreqhandle).read()

        if action ==1:
            crawled=re.findall("window.open\('([^']+)[^\)]*[^/]+\>([^0-9]+)\</a[^a]+a[^a]+a[^a]",tmpcontent)
            self.__crawled=crawled
            order=0
            self.__crawled=crawled
            for c in crawled:
                url,name=c
                print  order,name
                order+=1
                
            print "课程列表"
            
            

        if action==0:
            self.__save('shit_zf_xsxk_local.html',tmpcontent)
    def __choose_query(self,data):
        #查看某门课程
        data=int(data)
        crawled=self.__crawled[data][0]
        self.__info_url='http://'+self.__root_host+'/'+crawled
        self.__query_header['Referer'] = self.__xk_referer
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,None,self.__query_header)
        tmpcontent = tmpopener.open(tmpreqhandle).read().decode("gb2312").encode("utf-8")
        tmpregname=re.findall('jsxx[^\>]+xkkh=(\([^&]+)&[^\>]+\>(.+)\</[Aa]',tmpcontent)
        self.__xk_viewstate=re.findall('"__VIEWSTATE" value="([^"]+)"',tmpcontent)[0]
        #print self.__xk_viewstate
        #print tmpregname
        if tmpregname is []:
            print "出错,求退出"
        order=0
        self.__teachers=tmpregname

        for pair in tmpregname:
            xkkh,name=pair
            print order,xkkh,name
            order+=1
            
        print "请选择想选择的老师"
        #print self.__info_url,self.__xk_referer


        
    def __xsxjs_query(self,data):
        self.__xsxjs_data = {
            '__EVENTARGUMENT':'',
            }
        self.__xsxjs_data['xkkh']=data
        
        self.__xsxjs_data['__VIEWSTATE'] = self.__xk_viewstate
        self.__xsxjs_data['__EVENTTARGET']='Button1'
        self.__query_header['Referer']=self.__info_url

        
        self.__xsxjs_data = urllib.urlencode(self.__xsxjs_data)
        #print self.__xsxjs_data,self.__query_header

        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,self.__xsxjs_data,self.__query_header)
        tmpcontent = tmpopener.open(tmpreqhandle).read().decode("gb2312").encode("utf-8")
        
        msg=re.findall("alert\('([^']*)'",tmpcontent)[0]
        print msg,time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
        

    
    def user_query(self,info):
        self.__query_header = self.__login_header
        self.__query_header['HOST'] = self.__root_host
        self.__query_header['Referer'] = 'http://'+self.__root_host+'/xs_main_zzjk1.aspx?xh='+self.__username+'&type=1'

        if self.__mode==2:
            self.__mode=1
            print "已切换为查询模式"
            tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
            self.__tmpcontent=tmpopener.open(self.__query_header['Referer']).read().decode('gb2312').encode('utf-8')
            
        
        

        if(info[0] in [0,1,2]):
            
            tmpregurl = re.search('"xscjcx.aspx\?([^"]+)"',self.__tmpcontent)
            self.__info_url = 'http://'+self.__root_host+'/xscjcx.aspx?'+tmpregurl.group(1)
            self.__info_url = self.__info_url.decode('utf-8').encode('gb2312')
            self.__cjcx_query(info)

        elif(info[0] == 3):
            
            tmpregurl = re.search('"xskbcx.aspx\?([^"]+)"',self.__tmpcontent)
            self.__info_url = 'http://'+self.__root_host+'/xskbcx.aspx?'+tmpregurl.group(1)
            self.__info_url = self.__info_url.decode('utf-8').encode('gb2312')
            self.__ifcx_query('shit_zf_kbcx_local.html')

        elif(info[0] == 4):
            
            tmpregurl = re.search('"xskscx.aspx\?([^"]+)"',self.__tmpcontent)
            self.__info_url = 'http://'+self.__root_host+'/xskscx.aspx?'+tmpregurl.group(1)
            self.__info_url = self.__info_url.decode('utf-8').encode('gb2312')
            self.__ifcx_query('shit_zf_kscx_local.html')

        elif(info[0] == 5):
            
            tmpregurl = re.search('"xsdjkscx.aspx\?([^"]+)"',self.__tmpcontent)
            self.__info_url = 'http://'+self.__root_host+'/xsdjkscx.aspx?'+tmpregurl.group(1)
            self.__info_url = self.__info_url.decode('utf-8').encode('gb2312')
            self.__ifcx_query('shit_zf_djks_local.html')


    def user_option(self,option,data=''):
        #user_query method for  state machine in class choose
        self.__query_header = self.__login_header
        self.__query_header['HOST'] = self.__root_host
        self.__query_header['Referer'] = 'http://'+self.__root_host+'/xs_main_zzjk.aspx?xh='+self.__username+'&type=1'
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        content=tmpopener.open(self.__choose_url).read()
        has_choose=re.findall("xsxk.aspx",content)
        if has_choose is []:
            print "选课未开启"
            return 2
        if self.__mode==1:
            print "已切换为选课模式"
            self.__mode=2
            
        self.__query_header = self.__login_header
        self.__query_header['HOST'] = self.__root_host
        self.__query_header['Referer'] = 'http://'+self.__root_host+'/xs_main_zzjk.aspx?xh='+self.__username+'&type=1'
        
        if option==0:
            tmpregurl=re.findall('(xsxk.aspx[^"]+)',content)[0]
            self.__info_url='http://'+self.__root_host+'/'+tmpregurl+''
            self.__xk_referer=self.__info_url
            #self.__xk_referer=self.__xk_referer.decode("gb2312").encode("utf-8")
            self.__xsxk_query(0)
        elif option==1:
            tmpregurl=re.findall('(xsxk.aspx[^"]+)',content)[0]
            self.__info_url='http://'+self.__root_host+'/'+tmpregurl+''
            #self.__info_url=self.__info_url.decode("utf-8").encode("gb2312")
            self.__xk_referer=self.__info_url
            self.__xsxk_query(1)
        elif option==2:
            self.__choose_query(data)

        elif option==3:
            
            data=int(data)
            self.__xsxjs_query(self.__teachers[data][0])
            
            
            


    
    def __save(self,filename,content,simple=False):
        
        if simple is False:
            content=self.__get_style(content)
        tmpfp = open(filename,'w')
        tmpfp.write(content)
        tmpfp.close()

        if simple is True:
            return 
        
        browser=raw_input("是否用浏览器打开?(y/n)\n")
        if browser=='Y' or browser=='y':
            path=os.path.abspath(filename)
            webbrowser.open_new_tab('file://'+path)
        else:
            print filename+'已经保存到当前目录下'
    
    def __get_style(self,content):
        
        suffix={'css':[],'gif':[],'jpg':[],'js':[],'ico':[],'png':[],'jpeg':[]}
        
        for suffixkey in suffix.keys():
            tmpfilelist = re.findall('href="([^"]+\.'+suffixkey+')',content)
            suffix[suffixkey] = tmpfilelist
            tmpfilelist = re.findall('src="([^"]+\.'+suffixkey+')',content)
            suffix[suffixkey] += tmpfilelist

            self.__download(suffix[suffixkey])
            for filename in suffix[suffixkey]:
                content = re.sub('href="'+filename+'"','href="tmp/'+filename+'"',content)
                content = re.sub('src="'+filename+'"','src="tmp/'+filename+'"',content)
        
        tmpsrc = self.__get_inside_files(suffix['css'])
        self.__download(tmpsrc)

        return content
    
    def __get_inside_files(self,css):
        
        tmpret = []
        
        for filename in css:
            tmppath = 'tmp/'+filename
            try:
                tmpfp = open(tmppath)
            except:
                continue
            
            tmpcontent = tmpfp.read()
            tmpsrc = re.findall('url\(([^\)]+)\)',tmpcontent)
            tmpdir = '/'.join(filename.split('/')[:-1])+'/'
            
            for tmpiter in range(len(tmpsrc)):
                tmpsrc[tmpiter] = tmpdir + tmpsrc[tmpiter].lstrip('/')
                
            tmpret += tmpsrc
            
        return tmpret
            

    def __download(self,filelist):
        
        for tmpfilename in filelist:
            
            try:
                tmpopen = urllib2.urlopen('http://'+self.__root_host+'/'+tmpfilename)
            except:
                continue

            tmpdata = tmpopen.read()
            tmppath = 'tmp/'+tmpfilename
            directory = '/'.join(tmppath.split('/')[:-1])

            if os.path.exists(directory) != True:
                os.makedirs(directory)
            if os.path.exists(tmppath) != True:
                tmpfp = open(tmppath,"wb")
                tmpfp.write(tmpdata)
                tmpfp.close()

