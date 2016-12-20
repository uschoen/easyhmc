'''
Created on 16.05.2016

@author: uschoen
'''
from time import localtime, strftime
from datetime import datetime
from multilogger import *
import os
import threading

class core:
   
    def __init__(self, params):
        self.__config=params
        self.__output=[]
        self.__threadingLock=threading.Lock()
        self.__build_outputs(params['outputs'])
       
    def __build_outputs(self,outputs):
        for key in outputs:
            self.__build_output_intance(outputs[key])  
    def write(self,parms):
        dt = datetime.now()
        default_time=strftime("%d.%b %H:%M:%S", localtime())
        d_parms={   'time':default_time,
                    'microsecond':dt.microsecond,
                    'level':"unkown",
                    'package':"unkown",
                    'messages':"unkown",
                    'pid':"ukown"
                }
        d_parms.update(parms)
        parms['level']=str(parms['level'])
        parms['level'].lower()
        parms['pid']=os.getpid()
        self.__threadingLock.acquire()
        for logger in self.__output:
            logger.write(parms)
        self.__threadingLock.release()
    def __build_output_intance(self,output):
        if not output['enable']:
            return
        package=False
        if output['package']=="console":
            package=console.console(self.__build_config(output['config']))            
        elif output['package']=="file":
            package=file.file(self.__build_config(output['config']))
        else:
            print("kan not find pakage ".str(output['package']))
        if package:
            self.__output.append(package)
        
    def __build_config(self,output_config):
           
        default_package_filter={}
        default_loglevel_filter={}
        if "filter" in self.__config:
            default_filter=self.__config['filter']
            if "package" in default_filter:
                default_package_filter=default_filter['package']
            else:
                default_package_filter={'unkown':'true'}
            
            if "loglevel" in default_filter:
                default_loglevel_filter=default_filter['loglevel']
            else:
                default_loglevel_filter={'unkown':'true'}
        
        if "filter" in output_config:
            output_filter=output_config['filter']
            if not "package" in output_filter:
                output_config['filter']['package']=default_package_filter
                 
            if not "loglevel" in output_filter:
                output_config['filter']['loglevel']=default_loglevel_filter
        else:
            output_config['filter']={}
            output_config['filter']['package']=default_package_filter
            output_config['filter']['loglevel']=default_loglevel_filter
        return output_config
        
        
        