'''
Created on 16.05.2016

@author: uschoen
'''
from time import localtime, strftime
from datetime import datetime

class console:
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self.__config=params
    def write (self,parms):
       
        dt = datetime.now()
        default_time=strftime("%d.%b %H:%M:%S", localtime())
        d_parms={   'time':default_time,
                    'microsecond':dt.microsecond,
                    'level':"unkown",
                    'package':"unkown",
                    'messages':"unkown"
                }
        d_parms.update(parms)
        parms['level'].lower()
        if self.__filter(parms['package'],self.__config['filter']['package']):
            if self.__filter(parms['level'],self.__config['filter']['loglevel']):
                level=self.__colors(parms['level'])
                print ("%15s %6s %5s %10s %28s   "% (parms['time'],parms['microsecond'],parms['pid'],level,parms['package'])+str(parms['messages']))
    def __filter(self,string_log,filter_list={}):
        if string_log in filter_list:
            return filter_list[string_log]
        if "unkown" in filter_list:
            return filter_list["unkown"]
        else:
            return True         
    def __colors(self,string):
        if not "color" in self.__config:
            return string
        if not string in self.__config['color']:
            return string
        color=str(self.__config['color'][string])   
        CSI = "\x1B["
        CSI_OFF = "\x1B[0m"
        cl_string=CSI+color+string+CSI_OFF
        return cl_string
    
    
    
    
    
    
    