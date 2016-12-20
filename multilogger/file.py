'''
Created on 16.05.2016

@author: uschoen
'''
from time import localtime, strftime,time
from datetime import datetime
import os
import zipfile
import re


 
class file:
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self.__config={
                        'append':"false",
                        'dir':"/var/log/",
                        'filename':"EasyHMC.log",
                        'filesize':0,
                        'maxfiles':0
        }
        self.__config.update(params)
        
        self.__file=False
    def write (self,parms):
        dt = datetime.now()
        default_time=strftime("%d.%b %H:%M:%S", localtime())
        d_parms={   'time':default_time,
                    'microsecond':dt.microsecond,
                    'level':"unkown",
                    'package':"unkown",
                    'messages':"unkown",
                    'pid':"unkown"
                    
                }
        d_parms.update(parms)
        parms['level'].lower()
        if not self.__file:
            if not self.__file_open():
                return
        if self.__filter(parms['package'],self.__config['filter']['package']):
            if self.__filter(parms['level'],self.__config['filter']['loglevel']):            
                line=str(parms['time'])+"\t"+str(parms['microsecond'])+"\t"+str(parms['pid'])+"\t"+str(parms['level'])+"\t"+str(parms['package'])+"\t"+str(parms['messages'])+"\n" 
                self.__file.write(line)
                self.__file.flush()
                if self.__check_filesize():
                    self.__make_zip()
    def __file_open(self):
        try:
            filename= os.path.normpath(self.__config['dir']+self.__config['filename'])
            if self.__config['append']==True:
                self.__file= open(filename,'a+')  
            else:
                self.__file= open(filename,'w+')  
            return True
        except :
            print("Error: cant not open logfile, mode append:"+self.__config['append']+" file: "+filename)
            return False 
    def __file_close(self):
        if self.__file:
            self.__file.close()
            self.__file=False
    def __filter(self,string_log,filter_list={}):
        if string_log in filter_list:
            return filter_list[string_log]
        if "unkown" in filter_list:
            return filter_list["unkown"]
        else:
            return True 
    def __check_filesize(self):
        if self.__config['filesize']:
            log_file= os.path.normpath(self.__config['dir']+self.__config['filename'])
            filesize = os.path.getsize(log_file)
            if filesize>self.__config['filesize']*1024*1024:
                return True
        return False
    def __make_zip(self):
        if not self.__config['maxfiles']:
            return
        
        self.__file.close()
        filename= os.path.normpath(self.__config['dir']+self.__config['filename'])
        self.__check_count_zip()
        zipfile_name= os.path.normpath(self.__config['dir']+str(int(time()))+"_"+self.__config['filename']+".zip")
        zipper = zipfile.ZipFile(zipfile_name, 'w')
        zipper.write(filename,self.__config['filename'],zipfile.ZIP_DEFLATED)
        zipper.close()
        os.remove(filename)
        self.__file_open()
             
    def __check_count_zip(self):
        files = [f for f in os.listdir(self.__config['dir']) if re.match('\d{10}.'+self.__config['filename']+'.zip', f)]
        if len(files)<=self.__config['maxfiles']:
            return
        files.sort()
        anzahl=len(files)-self.__config['maxfiles']
        for file in files:
            os.remove(self.__config['dir']+file)
            anzahl=anzahl-1
            if anzahl==0:
                break
            
        
        
        
    