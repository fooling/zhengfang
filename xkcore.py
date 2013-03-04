#!/usr/bin/env python
#coding=utf-8

import re
import os
import urllib
import urllib2
import cookielib
import webbrowser
import random
import time

class cxcore(object):
    
    __root_host= 'ea.uestc.edu.cn'
    __host_list=[
        '222.197.164.82',
        '222.197.164.244',
        '222.197.165.148',
        '222.197.165.209',
        '222.197.165.74'
    ]
    
    __viewstates={}
    __state=''
    __trytime=0


    __mode=1

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

    def __xsxk_query(self,action=0):
        
        self.__xsxk_data = {
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            'xx':'',
            }

        print self.__info_url
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__info_url,None,self.__query_header)
        tmpcontent='防刷'

        # for kidding
        while re.findall('防刷',tmpcontent) !=[]:
            tmpcontent = tmpopener.open(tmpreqhandle).read().decode('gb2312').encode('utf-8')
            print tmpcontent
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
        tmpcontent = tmpopener.open(tmpreqhandle,self.__xsxk_data).read()
        
        self.__save('shit_zf_xsxk_local.html',tmpcontent)
    
    def user_query(self,info):
        
        self.__query_header = self.__login_header
        self.__query_header['HOST'] = self.__root_host
        self.__query_header['Referer'] = 'http://'+self.__root_host+'/xs_main_zzjk1.aspx?xh='+self.__username+'&type=1'

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
            self.__xsxk_query(0)
        elif option==1:
            tmpregurl=re.findall('(xsxk.aspx[^"]+)',content)[0]
            self.__info_url='http://'+self.__root_host+'/'+tmpregurl+''
            self.__xsxk_query(1)
            
            
            
    


    
    def __save(self,filename,content):
        
        content=self.__get_style(content)
        tmpfp = open(filename,'w')
        tmpfp.write(content)
        tmpfp.close()
        
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

