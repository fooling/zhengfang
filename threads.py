#-*-  coding:utf-8 -*-


from threading import Thread

class ChooseOneThreads(Thread):

    def __init__(self,handler):
        Thread.__init__(self)
        
