'''
Created on 18.12.2016

@author: uschoen
'''
__version__ = "1.9"


from time import localtime, strftime,sleep
from datetime import datetime
import MySQLdb

class server(object):
    '''
    classdocs
    '''


    def __init__(self,parms,core,logger=False):
        '''
        Constructor
         '''
        self.__core=core
        self.__config={}
        self.__config.update(self.__loadDefaultArgs())
        self.__config.update(parms)
        self.__logger=logger 
        self.__dbConnection=False
        self.__log("debug","build  %s instance"%(__name__))
    def callback(self,device):
        if not self.__dbConnection:
            self.__dbConnect()
        self.__log("debug","callback from device id %s"%(device.getAttributeValue('deviceID')))
        fieldstring=""
        valuestring=""
        secound=False
        
        for fields in self.__config['mapping']:
            for key in fields:
                if secound:
                    fieldstring+=","
                    valuestring+=","
                secound=True
                fieldstring+=("`%s`"%(key))
                valuestring+=("'%s'"%(device.getAttributeValue(fields[key])))
        sql=("INSERT INTO `%s` (%s) VALUES (%s)"%(self.__config['table'],fieldstring,valuestring))
        self.__log("debug","build sql string:%s"%(sql))
        try:
            with self.__dbConnection:
                cur = self.__dbConnection.cursor()
                cur.execute(sql)
        except MySQLdb.ProgrammingError as e:
            self.__log("error","ProgrammingError"%(e))
        except MySQLdb.OperationalError as e:
            self.__log("error","OperationalError%s"%(e))
            
    def __dbConnect(self):
        self.__log("info","try connect to host:%s with user:%s table:%s"%(self.__config['host'],self.__config['user'],self.__config['db']))
        try:
            self.__dbConnection = MySQLdb.connect(
                                                  host=self.__config['host'],
                                                  db=self.__config['db'],
                                                  user=self.__config['user'], 
                                                  passwd=self.__config['password']
                                                  )
            self.__dbConnection.apilevel = "2.0"
            self.__dbConnection.threadsafety = 2
            self.__dbConnection.paramstyle = "format" 
            self.__log("info","connect succecfull")
            return
        except MySQLdb.DataError as e:
            print("DataError"%(e))
            print(e)
         
        except MySQLdb.InternalError as e:
            self.__log("InternalError"%(e))
        except MySQLdb.IntegrityError as e:
            self.__log("IntegrityError"%(e))
        except MySQLdb.OperationalError as e:
            self.__log("error","OperationalError%s"%(e))
        except MySQLdb.NotSupportedError as e:
            self.__log("error","NotSupportedError"%(e))
        except MySQLdb.ProgrammingError as e:
            self.__log("error","ProgrammingError"%(e))
        except:
            self.__log("error","Unknown error occurred")
                
    def __dbClose(self):
        if self.__dbConnection:
            self.__log("info","close database")
            self.__dbConnection.close()    
    def __loadDefaultArgs(self):
        args={"host":"127.0.0.1",
             "user":"SQLUSER",
             "password":"",
             "db":"hmc",
             "table":"statistic",
             "mapping":[]
             }
        return args
    def __log (self,level="unkown",messages="no messages"):
        if self.__logger:
            dt = datetime.now()
            conf={}
            conf['package']=__name__
            conf['level']=level
            conf['messages']=str(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self.__logger.write(conf)   
            
            
            
            
if __name__ == "__main__":            
    class logger(object):
        def write(self,arg):
            print arg['messages']
    
    
    args={"host":"192.168.3.100",
             "user":"hmceasy",
             "password":"test1",
             "db":"hmc",
             "table":"statistic",
             "mapping":
               [
                 {"value":"value"},
                 {"deviceid":"device"},
                 {"lastchange":"timestamp"}
               ] }
    core=False
    mapper = server(args,core,logger())
    print("start")
    print("mysql mapper  build")
    while True:
        print("main wait 10 sec")
        sleep(10) 
'''
sudo apt-get install python-mysqldb
'''        