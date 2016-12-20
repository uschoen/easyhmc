'''
Created on 21.10.2016

@author: uschoen

sudo apt-get install rrdtool python-rrdtool

'''
__version__ = "1.9"

import threading,os,re
from time import localtime, strftime,sleep
from datetime import datetime
import socket


class sensor(threading.Thread): 
    def __init__(self, params,core,logger=False):
        threading.Thread.__init__(self)
        self.__core=core
        self.__config=params
        self.__logger=logger
        self.running=1
        self.__config['host']=str(socket.gethostbyaddr(socket.gethostname())[0])
        self.__connected_senors={}
        self.__log("debug","build  "+__name__+" instance")
    
    def run(self):
        self.__log("info",__name__+"  start")
        while self.running:
            self.__checkConnectedDevices()
            for sensorID in self.__config["devices"]:
                deviceID="%s@%s.%s"%(sensorID,self.__config['gateway'],self.__config['host'])
                if  self.__config["devices"][sensorID]==False or self.__core.getDeviceAttributeValue(deviceID,"enable")==False:
                    self.__log("info","sensor %s / deviceID%s is disconnected or not enable"%(sensorID,deviceID))
                    continue    
                path=self.__config["path"]+sensorID+"/w1_slave"
                SensorValue=self.__read_sensor(path)
                if SensorValue=="U":
                    self.__log("error","sensor id %s send wrong value. ignore"%(sensorID))
                    continue
                self.__updateDevice(deviceID,round(float(SensorValue),2))
            self.__log("info","wait "+str(self.__config["intervall"])+" for next scan")  
            sleep(self.__config["intervall"])    
        self.__log("warning",__name__+"  pause")
    '''
        update davice if change
    ''' 
    def __updateDevice(self,deviceID,value):
        self.__log("debug","update deviceID %s with value:% s"%(deviceID,value))
        oldTemperatur=float(self.__core.getValue(deviceID))
        self.__log("debug","old value: %s new value: %s temp div:%s"%(oldTemperatur,value,self.__config["tempDiv"])) 
        if oldTemperatur < (value-float(self.__config["tempDiv"])) or oldTemperatur > (value+float(self.__config["tempDiv"])):
            self.__log("info","temperatur is change more than %s C"%(self.__config["tempDiv"]))
            self.__core.setValue(deviceID,value)                   
        else:
            self.__log("debug","temperatur is not change")   
    '''
        check if new devices connected or disconnected
    '''
    def __checkConnectedDevices(self):
        self.__log("debug","check connected devices")
        self.__disableAllDevices()
        self.__scanDevices()
        self.__deleteDisconectedDevices()
    '''
        scan for new devices
    '''
    def __scanDevices(self):
        self.__log("debug","read connected devices on path %s"%(self.__config["path"]))
        
        if os.path.exists(self.__config["path"]):
            SensorList =os.listdir(self.__config["path"])
            for sensorID in SensorList:
                if sensorID=="w1_bus_master1":
                    self.__log("debug","ignore sensor %s"%(sensorID))
                    continue
                if re.search("00000000",sensorID):
                    self.__log("debug","ignore sensor %s"%(sensorID))
                    continue
                if sensorID in self.__config["devices"]:
                    self.__log("debug","find exiting sensor %s"%(sensorID))
                    self.__config["devices"][sensorID]=True
                else:
                    self.__log("debug","find new sensor %s"%(sensorID))
                    self.__config["devices"][sensorID]=True
                    self.__addNewDevice(sensorID)
        else:
            self.__log("error","no path found %s forgot to install onewire?"%(self.__config["path"]))      
    '''
        disable all devices in list 
    '''
    def __disableAllDevices(self):
        self.__log("debug","disable all devices")
        for sensorID in self.__config["devices"]:
            self.__config["devices"][sensorID]=False
    ''' 
        add new sensor in CORE
    '''
    def __addNewDevice(self,sensorID):
        deviceID="%s@%s.%s"%(sensorID,self.__config['gateway'],self.__config['host'])
        self.__log("debug","add new sensor %s with devicesID:%s"%(sensorID,deviceID))        
        if not deviceID in self.__core.getAllDeviceId():
            self.__core.addDevice(deviceID,"ds1820")
        else:
            self.__log("info","devices ID %s is existing"%(deviceID))    
    '''
        delete all disconnect Devices intern
    ''' 
    def __deleteDisconectedDevices(self):
        self.__log("debug","delete disconnected devices")
        for sensorID in self.__config["devices"]:
            if not self.__config["devices"][sensorID]:
                del self.__config["devices"][sensorID]
                self.__log("info","delete disconnected sensorID %s"%(sensorID))
    '''
        reading sensor value
    '''
    def __read_sensor(self,path):
        value = "U"
        try:
            f = open(path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value = str(float(m.group(2)) / 1000.0)
                    f.close()
        except IOError:
            self.__log("error","can not read sensor id"+ str(path))
        return value
    
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
'''
Enable onewire
>Kernel 3.18 (Februar 2015)
login with user: pi
->sudo nano /boot/config.txt
insert at the end of the file

dtoverlay=w1-gpio,gpiopin=4,pullup=on

save, and reboot
->sodo reboot

after reboot login with user: pi

->sudo modprobe w1-gpio pullup=1
->sudo modprobe w1-therm       

for autmomatik start the onewire cahnge the file /etc/modules
->sudo nano /etc/modules
and insert at the end of the file

w1-gpio pullup=1
w1-therm
     
        
        
   
'''   
            