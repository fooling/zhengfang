#-*- coding=utf-8 -*-


#main.py   -state machine version

import getpass
import state
import xkcore as core
import os
import json

flag = 'r'


if os.path.exists("userfile.tmp") == False:
    print '请输入你的学号'
    username = raw_input('> ')
    print '请输入你的密码'
    password = getpass.getpass('> ')
    save=raw_input('是否保存(y/n)')
    if save=='y' or save=='Y':
        tfp=open("userfile.tmp","w")
        data={'username':username,'password':password}
        content=json.dumps(data).encode('utf-8')
        tfp.write(content)
        tfp.close()
else:
    r=open("userfile.tmp")
    c=r.read()
    r.close()
    data=json.loads(c)
    username=data['username']
    password=data['password']

userinfo = core.cxcore(username,password)

stat=state.StateMachine(userinfo)

while(flag == 'r'):
    
    print '选择你所需要的功能：'
    print '0、成绩查询  1、课表查询  2、考试查询  3、等级考试查询'
    print '4、退出  6 列出已选课程  7 列出可选课程' 
    print '8 下载所有课表'
    choose = raw_input('> ')

    flag=stat.run(choose) 

    
