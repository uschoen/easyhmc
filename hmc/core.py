'''
Created on 06.12.2016

@author: uschoen
'''

__version__ = "1.2"

from time import localtime, strftime,sleep,time
from datetime import datetime
import importlib
import sys
from hmcDevices import *
import json


class manager(object): 
       
       
    def __init__(self,args,logger):
        self.__args=args
        self.__logger=logger
        self.__deviceList={}
        self.__callbackList={}
        self.__eventHandlerList={}
        self.__defaultEventHandlerList={
                        "oncreate_event":[],                
                        "ondelete_event":[],
                        "onrefrech_event":[],
                        "onchange_event":[],
                        "onboot_event":[],
                        "onshutdown_event":[]                
                                        }
        self.__log("info","build %s instance version %s"%(__name__,__version__))
        self.readBackup()
    '''
    ################################
    Devices
    ################################
    '''    
    
    def addDevice(self,deviceID,deviceType):
        self.__log("info","add device with device id %s and typ:%s"%(deviceID,deviceType))
        if deviceID in self.__deviceList:
            self.__log("error","device id %s is existing"%(deviceID))
            return False
        self.__loadDevice(deviceID,deviceType,False)
    def restoreDevice(self,deviceID,deviceType,args=False):
        self.__log("info","restore device with device id %s and typ:%s"%(deviceID,deviceType))
        if deviceID in self.__deviceList:
            self.__log("error","device id %s is existing"%(deviceID))
            return False
        self.__loadDevice(deviceID,deviceType,args)
    def deleteDevice(self,deviceID):
        self.__log("info","delteDevice for device id %s"%(deviceID))
        if not deviceID in self.__deviceList:
            self.__log("error","defice id %s not existing"%(deviceID))
            return False
        del self.__deviceList[deviceID]
        self._ondelete_event(deviceID)
        '''
         return a list with all object IDs
        '''
    def getAllDeviceId(self):  
        object_list=list()
        for object_id in self.__deviceList:
            object_list.append(object_id)
        return object_list
    
    
    
    def addParameter(self,device_id,paramter,value):
        self.__log("info","addParameter for device id %s"%(device_id))
        if not device_id in self.__deviceList:
            self.__log("error","defice id %s not existing"%(device_id))
            return False
    
    
   
    
    def setValue(self,deviceID,value):
        self.__log("info","setValue for device id %s value %s"%(deviceID,value))
        if not deviceID in self.__deviceList:
            self.__log("error","device id %s not existing"%(deviceID))
            return False
        self.__deviceList[deviceID].setValue(value)
    def getValue(self,deviceID):
        self.__log("info","getValue for device id %s"%(deviceID))
        if not deviceID in self.__deviceList:
            self.__log("error","device id %s not existing"%(deviceID))
            return False
        return self.__deviceList[deviceID].getValue()
    def getEvents(self,device_id):
        self.__log("info","getEvents for device id %s"%(device_id))
        if not device_id in self.__deviceList:
            self.__log("error","device id %s not existing"%(device_id))
            return False
    def getFuntionen(self,device_id):
        self.__log("info","getFunktion for device id"%(device_id))
        if device_id not in self.__deviceList:
            self.__log("error","device id %s not existing"%(device_id))
            return False
    
    '''
    #######################
    eventHandler
    #######################
    '''    
    def addEventHandler(self,eventHandler,name):  
        self.__log("debug","adding eventhandler %s"%(name))
        if name in self.__eventHandlerList:
            self.__log("error","eventHandler %s is existing"%(name)) 
        self.__eventHandlerList[name]=eventHandler       
    '''
    ####################### 
    Attribute Handling
    #######################
    '''
    def setDeviceAttributeValue(self,objectID,attribut,value): 
        if objectID not in self.__deviceList:
            self.__log("error","object id %s not existing"%(objectID))
            return False
        self.__log("debug","object id %s set parameter %s to value:%s"%(objectID,attribut,value))
        self.__deviceList[objectID].setAttributeValue(attribut,value)
    def getDeviceAttributeValue(self,deviceID,attribut): 
        if deviceID not in self.__deviceList:
            self.__log("error","object id %s not existing"%(deviceID))
            return False
        return self.__deviceList[deviceID].getAttributeValue(attribut)
    
    def getAllDeviceAttribute(self,deviceID): 
        '''
        return a list with all avaible attribute
        '''
        if deviceID not in self.__deviceList:
            self.__log("error","object id %s not existing"%(deviceID))
            return False
        return self.__deviceList[deviceID].getAllAttribute()  
    
    '''
    #########################
    System funktionen
    #########################
    '''
    '''
    add default event to new devices
    '''
    def __registerDefaultEvents(self,deviceID):
        for eventName in self.__defaultEventHandlerList:
            self.__deviceList[deviceID].registerEventHandler(eventName,self.__defaultEventHandlerList[eventName])
    '''
    write backup to file
    '''        
    def writeBackup(self):
        configFile=self.__args['configurationFile']
        backup={}
        self.__log("info","write backup to %s "%(configFile))
        configuration={}
        with open( configFile,'w') as outfile:
            for deviceID in self.getAllDeviceId():
                allAttribute={}
                self.__log("data","find object in CORE:%s"%(deviceID))
                allAttribute=self.__deviceList[deviceID].getConfiguration()
                configuration[deviceID]=allAttribute
            backup['devices']=configuration
            dummy={}
            backup['defaultEventHandlerList']=self.__defaultEventHandlerList
            json.dump(backup, outfile,sort_keys=True, indent=4)
            outfile.close()
    '''
    restore data
    '''
    def readBackup(self):
        self.__log("info","read backup from %s "%(self.__args['configurationFile']))
        try:
            backup=self.__loadConfiguration(self.__args['configurationFile'])
        except IOError:
            self._log("error","can not find %s file"%(self.__args['configurationFile']))  
            return  
        except :
            self._log("error","can not load %s file"%(self.__args['configurationFile']))  
            return
        ''' restore defaultEventHandlerList '''
        if "defaultEventHandlerList" in backup:
            self.__defaultEventHandlerList= backup['defaultEventHandlerList']
        ''' restore devices '''
        if "devices" in backup:
            tempConfiguration=backup['devices']
            for deviceID in tempConfiguration:
                self.__log("info","restore deviceID: %s with typ %s  "%(deviceID,tempConfiguration[deviceID]['typ']['value']))
                self.restoreDevice(deviceID,tempConfiguration[deviceID]['typ']['value'],tempConfiguration[deviceID])
    def __loadConfiguration(self,file):
        self.__log("debug","load attribute %s"%(file)) 
        try:
            with open(file) as json_data_file:
                data = json.load(json_data_file)
                return data 
        except IOError:
            self.__log("error","can not find %s"%(file))
            return {} 
        except :
            self.__log("error","can not load %s"%(file)) 
            return {}    
    def callFunktion(self,device_id,function,parameter):
        self.__log("info","callFunktion %s for device id %s parameter %s "%(function,device_id,parameter))
        if device_id not in self.__deviceList:
            self.__log("error","defice id %s not existing"%(device_id))
            return False
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
    def __loadDevice(self,deviceID,deviceTyp,attribute=False):
        self.__log("info","add new device %s"%(deviceTyp))
        pakageName="hmc.hmcDevices."+str(deviceTyp)
        self.__log("info","try to load %s"%(pakageName))
        adding=False
        if not attribute:
            adding=True
            attribute={'deviceID':{
                            "value":deviceID
                            },
                 'typ':{
                            "value":deviceTyp
                            }
                } 
        argumente=(attribute,self.__logger,self.__eventHandlerList,adding)
        try:
            module = importlib.import_module(pakageName)
            className = "device"
            self.__deviceList[deviceID] = getattr(module, className)(*argumente)
            if hasattr(module, '__version__'):
                if module.__version__<__version__:
                    self.__log("warning", "Version of %s is %s and can by to low"%(pakageName,module.__version__))
                else:
                    self.__log("info", "Version of %s is %s"%(pakageName,module.__version__))
            else:
                self.__log("warning", "pakage %s has no version Info"%(pakageName))       
        except ImportError:
            self.__log("warning", "deviceTyp %s no found use hmcDefault typ"%(deviceTyp))
            pakageName="hmc.hmcDevices.hmcDevices"
            module = importlib.import_module(pakageName)
            className = "defaultDevice"
            self.__deviceList[deviceID] = getattr(module, className)(*argumente)
            if hasattr(module, '__version__'):
                if module.__version__<__version__:
                    self.__log("warning", "Version of %s is %s and can by to low"%(pakageName,module.__version__))
                else:
                    self.__log("info", "Version of %s is %s"%(pakageName,module.__version__))
            else:
                self.__log("warning", "pakage %s has no version Info"%(pakageName)) 
        except :
            self.__log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.__log("error","Traceback Info:" + str(msg))  


if __name__ == "__main__":

    class logger(object):
        def write(self,arg):
            print arg['messages']
    
    
    args={'configurationFile':'data/devices.json'}
    cor = manager(args,logger())
    print("start")
    print("core build")
    cor.addDevice( "ks300_temperatur@host.de","ks300_temperatur")
    cor.setValue("ks300_temperatur@host.de", "76,9")
    while True:
        print("main wait 10 sec")
        sleep(10) 