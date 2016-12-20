#!/usr/bin/python
'''
Created on 16.11.2016

@author: uschoen
'''
__version__ = "1.6"

import sys 
import importlib
import getopt
import os
import json
import getpass
import traceback
from datetime import datetime
import time
from multilogger import dispatcher
from hmc import *
from gateways import *
from eventHandler import *




def usage():
    '''
    command line menu for -help --h
    '''
    print sys.argv[0], "--config=configfile [--daemon] "
    print sys.argv[0], "--help (-h) this menu"
    print sys.argv[0], "--version (-v) show version of HMC"
    print sys.argv[0], "--daemon (-d) run as daemon"


def my_exception(exc_type, exc_value, exc_traceback):
    
    """ 
    handle all exceptions 
    """
    global logger,log
    if issubclass(exc_type, KeyboardInterrupt):
        filename, line, dummy, dummy = traceback.extract_tb( exc_traceback ).pop()
        filename = os.path.basename( filename )
        error    = "%s: %s" % ( exc_type.__name__, exc_value )
        if logger:
            log("Error","a critical error has occured:%s" %(error))
            log("Error","It occurred at line %d of file %s" % (line, filename))
            log("error","".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        else:
            print("a critical error has occured:%s" %(error))
            print("It occurred at line %d of file %s" % (line, filename))
            print "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    exit(0)

def loadEventHandler(eventHandlerList):
    global coreInstance
    for eventHandlerName in eventHandlerList:
        if not eventHandlerList[eventHandlerName]['enable']:
            log("info","event handler :%s is disable"%(eventHandlerName))
            continue
        pakage="eventHandler."+eventHandlerList[eventHandlerName]['pakage']+"."+eventHandlerList[eventHandlerName]['modul']
        log("info","try to load event handler:%s with pakage: %s"%(eventHandlerName,pakage))
        ARGUMENTS = (eventHandlerList[eventHandlerName]['config'],coreInstance,logger)  
        try:
            module = importlib.import_module(pakage)
            CLASS_NAME = eventHandlerList[eventHandlerName]['class']
            coreInstance.addEventHandler((getattr(module, CLASS_NAME)(*ARGUMENTS)),eventHandlerName)
            if hasattr(module, '__version__'):
                if module.__version__<__version__:
                    log("warning", "Version of %s is %s and can by to low"%(pakage,module.__version__))
                else:
                    log("info", "Version of %s is %s"%(pakage,module.__version__))
            else:
                log("warning", "pakage %s has no version Info"%(pakage))
        except :
            log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                log("error","Traceback Info:%s"%(msg))  

def loadThread(threadList):
    threadInstance={}
    for threadName in threadList:
        if not threadList[threadName]['enable']:
            log("info","gateway:%s is disable"%(threadName))
            continue
        pakage="gateways."+threadList[threadName]['pakage']+"."+threadList[threadName]['modul']
        log("info","try to load gateway:%s with pakage: %s"%(threadName,pakage))
        ARGUMENTS = (threadList[threadName]['config'],coreInstance,logger)  
        try:
            module = importlib.import_module(pakage)
            CLASS_NAME = threadList[threadName]['class']
            threadInstance[threadName] = getattr(module, CLASS_NAME)(*ARGUMENTS)
            if hasattr(module, '__version__'):
                if module.__version__<__version__:
                    log("warning", "Version of %s is %s and can by to low"%(pakage,module.__version__))
                else:
                    log("info", "Version of %s is %s"%(pakage,module.__version__))
            else:
                log("warning", "pakage %s has no version Info"%(pakage))
            
            threadInstance[threadName].daemon = True
        except :
            log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                log("error","Traceback Info:%s"%(msg))
    return threadInstance              
def getOptions():
    '''
    check command line argument
    --h -help helpmenu
    --v -version show version
    --d -daemon run as daemon, default false
    --c -config config file, default etc/config.json
    '''
    shortOptions = 'hdvc:'
    longOptions = ['help', 'version','config=', 'daemon']
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortOptions, longOptions)
        return opts
    except getopt.GetoptError:
        print "please use:"
        usage()
        sys.exit()
        
def loadConfigurationFile(file):
    '''
    loading configuration file
    '''
    try:
        with open(os.path.normpath(file)) as jsonDataFile:
            dateFile = json.load(jsonDataFile)
        return dateFile 
    except IOError:
        print ('cant not find file: '+os.path.normpath(file))
        sys.exit()
    except ValueError:
        e = sys.exc_info()[1]
        print ('error in config file: '+os.path.normpath(file))
        print("error: %s" % e )
        sys.exit()
    except :
        print("UNKOWN ERROR in script: %s" % sys.exc_info()[0] )
        sys.exit()

def log (level="unkown",messages="no messages"):
    '''
    logger converter
    '''
    global logger
    if logger:
        dt = datetime.now()
        meassage={}
        meassage['package']=__name__
        meassage['level']=level
        meassage['messages']=messages
        meassage['time']=time.strftime("%d.%b %H:%M:%S", time.localtime())
        meassage['microsecond']=dt.microsecond
        logger.write(meassage)
        
''' 
Gloable Variablen
'''
configuration={
               'configfile':'etc/config.json',
               'daemon':False              
              }        
logger=False
CoreInstance=False
allThreads={}
eventHandler={}

'''
global handle
'''
sys.excepthook = my_exception
'''
start up
load ommand line option
'''        
for o, a in getOptions():
    if o == "--help" or o == "-h":
        print "HELP:"
        usage()
        sys.exit()
    elif o == "--config" or o == "-c":
        print "use config file:", a
        configuration['configfile']=a
    elif o == "--daemon" or o== "-d":
        print "run as daemon:", a
        configuration['daemon']=True
    elif o == "--version" or o=="-v":
        print (__version__)
        sys.exit()
'''
load configuration
'''
configuration.update(loadConfigurationFile(configuration['configfile']))

'''
add multilogger 
'''
if 'multilogger' in configuration:
    if configuration['multilogger']['enable']:
        logger=dispatcher.core(configuration['multilogger'])
log("info", "startup and run under user:"+str(getpass.getuser())) 
log("info", "EasyHMC Version: %s"%(__version__)) 

'''
build cor 
'''
coreInstance=core.manager(configuration['core'],logger)

''' 
load eventHadler
'''
loadEventHandler(configuration['eventHandler'])

''' 
start up Gateways
'''
allThreads.update(loadThread(configuration['gateways']))

'''
start ....
'''





''' 
start threads
'''
log("info", "find %d threads to start"%(len(allThreads)))
for threadsToStart in allThreads:
    log("info", "starting thread: %s"%(threadsToStart))
    allThreads[threadsToStart].start()
    
log("info","HMC monitoring threads")  
''' 
check threads
'''


try:
    while 1:
        '''
        for deviceID in coreInstance.getAllDeviceId():
            log("data","find object in CORE:%s"%(deviceID))
            for attribute in coreInstance.getAllDeviceAttribute(deviceID):
                
                #log("data","%s : %s"%(attribute,coreInstance.getDeviceAttributeValue(deviceID,attribute)))
          '''
        for threadsTocheck in allThreads:        
            if allThreads[threadsTocheck].isAlive():
                log("info", "thread: "+threadsTocheck+" is alive")
            else:
                log("error", "thread: "+threadsTocheck+" not running")
      
        time.sleep(60) 
    log("emergency", "HMC not running and stop")
except KeyboardInterrupt:
    log("emergency","control C press!!,system goaing down !!")  
except :
    log("error",sys.exc_info())
    tb = sys.exc_info()
    for msg in tb:
        log("error","Traceback Info:" + str(msg)) 
finally:
    log("emergency","system goaing down !!")
    coreInstance.writeBackup()
    



        

