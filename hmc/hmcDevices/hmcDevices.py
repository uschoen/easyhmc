'''
Created on 05.12.2016

@author: uschoen
'''
__version__="1.9"

from time import localtime, strftime,time,sleep
from datetime import datetime
import json


class defaultDevice(object):
    '''
    classdocs
    '''

    ''' 
        contructor
    '''
    def __init__(self,arg,logger,eventHandlerList,adding):
        self.__eventHandlerList=eventHandlerList
        self._logger=logger
        self._attribute={}
        self._attribute.update(self._load_attribute("hmc/hmcDevices/hmcDevices.json"))
        self._attribute.update(self._load_attribute("hmc/hmcDevices/"+self._name_()+".json"))
        self._attribute.update(arg)
        self._log("debug","build %s instance"%(self._name_()))
        if adding:
            self._oncreate_event()
             
    '''
     get value 
     public function
    '''
    def getValue(self):
        self._log("debug","get  value  for id:"+self._attribute['deviceID']['value'])
        return self._attribute['value']['value']
    '''
     set value 
     public function
    '''
    def setValue(self,Value):
        self._log("debug","set sensor data to %s"%(Value))
        if Value==self._attribute['value']['value']:
            self._onrefresh_event()
        else:
            self._attribute['value']['value']=Value 
            self._onrefresh_event()
            self._onchange_event() 
    
    '''
    ####################
    Attribute section
    ####################
    '''
            
    '''
    get parameter
    public function
    '''    
    def getAllAttribute(self):
        self._log("debug","get all attribute for device:%s"%(self._attribute['deviceID']['value']))
        attribute_list=[]
        for key in self._attribute:
            if not "hidden" in self._attribute[key]:
                attribute_list.append(key)
        return attribute_list
    '''
    add attribut
    internel function
    '''    
    def addAttribute(self,parameter,value):
        self._log("debug","set sensor data")
    '''
    get value of attribut
    public function
     '''    
    def getAttributeValue(self,attribute):
        self._log("debug","get attribut value for:%s"%(attribute))
        if not attribute in self._attribute:
            self._log("error","can not find attribut:%s "%(attribute))
            return False
        return self._attribute[attribute]['value']
    '''
     set value of attribut
     public function
     '''    
    def setAttributeValue(self,parameter,value):
        if not parameter in self._attribute:
            self._log("error","arameter %s to not exist"%(parameter))
        self._log("debug","set parameter %s to %s"%(parameter,value))
        self._attribute[parameter]['value']=value 
    def getConfiguration(self):
        return self._attribute
    '''
    ####################
    Events
    internel function
    ####################
    '''
    def registerEventHandler(self,eventTyp,eventName):
        self._log("debug","register new event handler %s for event %s"%(eventTyp,eventName))
        self._attribute['eventTyp']['value'].append(eventName)
        
    def _onchange_event(self):
        self._log("debug","__onchange_event: %s"%(self._attribute['deviceID']['value']))
        self._attribute['lastchange']['value']=int(time())
        for eventName in self._attribute["onchange_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _onrefresh_event(self):
        self._log("debug","__onrefresh_event: %s"%(self._attribute['deviceID']['value']))
        self._attribute['lastupdate']['value']=int(time())
        for eventName in self._attribute["onrefresh_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _onboot_event(self):
        self._log("debug","__onboot_event: %s"%(self._attribute['deviceID']['value']))
        for eventName in self._attribute["onboot_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _oncreate_event(self):
        self._log("debug","__oncreate_event: %s"%(self._attribute['deviceID']['value']))
        self._attribute['create']['value']=int(time())
        for eventName in self._attribute["oncreate_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _ondelete_event(self):
        self._log("debug","__ondelete_event: %s"%(self._attribute['deviceID']['value']))
        for eventName in self._attribute["ondelete_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    '''
    ####################
    logging
    internel function
    ####################
    '''
    def _log (self,level="unkown",messages="no messages"):
        if self._logger:
            dt = datetime.now()
            conf={}
            conf['package']=__name__
            conf['level']=level
            conf['messages']=self._name_()+":"+str(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self._logger.write(conf)
    def _name_(self):
        return "hmcDevices"
    def _load_attribute(self,file):
        self._log("debug","load attribute  "+file)  
        try:
            with open(file) as json_data_file:
                data = json.load(json_data_file)
                return data['attribute'] 
        except IOError:
            self._log("error","can not find "+self._name_()+".json file")   
            raise 
        except :
            self._log("error","can not load "+self._name_()+".json file") 
            raise
    '''    
    
    
if __name__ == "__main__":

    
    class logger(object):
        def write(self,arg):
            print arg['messages']
    loging=logger()
    arg={'deviceID':{
                        "value":"test@test.test"
                        },
             'typ':{
                        "value":"hmcDevices"
                        }
            }
    hmcDevice = defaultDevice(arg,loging)
    print("build hmc object")
    print("start thread")
    hmcDevice.setValue(90)
    hmcDevice.setParameterValue("rssi", -98)
    while True:
        print("main wait 10 sec")
        sleep(10)    
'''