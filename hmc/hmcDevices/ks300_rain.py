'''
Created on 05.12.2016

@author: uschoen
'''
from hmcDevices import defaultDevice
from time import time,sleep


__version__="1.9"

class device(defaultDevice):
    '''
    classdocs
    '''   
    def _name_(self):
        return "ks300_rain"    
    
    def setValue(self,RAWvalue):
        '''
        check ist rain  value have change
        '''
        self.__rainMM=0.2469
        self.__clearOldRain()
        if self._attribute['firststart']['value']:
            self._attribute['lastrain']['value']=RAWvalue
            self._attribute['firststart']['value']=False
            self._log("debug","set  "+self._name_()+" firststart to false") 
            return
        
        if RAWvalue==self._attribute['lastrain']['value']:
            self._onrefresh_event()
            return
        
        rainDelta=RAWvalue-self._attribute['lastrain']['value']
        
        self._log("debug","RAWvalue:%s lastRAWvalue:%s delta:%s"%(RAWvalue,self._attribute['lastrain']['value'],rainDelta))
        
        if rainDelta<0:
            self._log("error","rain delta negativ") 
            
        self._attribute['lastrain']['value']=RAWvalue
        self._attribute['value']['value']=rainDelta*self.__rainMM 
        self._log("data", "rain set to %s"%(self._attribute['value']['value']))
        self._attribute['lastrain24']['value'][int(time())]=float(rainDelta*self.__rainMM)
        self._attribute['lastrain1h']['value'][int(time())]=float(rainDelta*self.__rainMM)
        self._attribute['rain24h']['value']=self.__calcRain24mm()
        self._attribute['rain1h']['value']=self.__calcRain1hmm()
        
        self._onrefresh_event()
        self._onchange_event()
    
    def __clearOldRain(self):
        timebefor24=int(time())-86400
        timebefor1h=int(time())-3600
        self._attribute['lastrain1h']['value']={}
        self._log("debug","clear rain data where older then %s"%(timebefor24))
        for rainTimeStamp in self._attribute['lastrain24']['value']:
            self._log("data","time rain %s < %s befor"%(rainTimeStamp,timebefor24))
            if rainTimeStamp>timebefor1h:
                self._attribute['lastrain1h']['value'][rainTimeStamp]= self._attribute['lastrain24']['value'][rainTimeStamp]
            if rainTimeStamp<timebefor24:
                del  self._attribute['lastrain24']['value'][rainTimeStamp]
                self._log("debug","delete rain data with time %s"%(rainTimeStamp))   
    def __calcRain24mm(self):
        rain24=0
        for rainTimeStamp in self._attribute['lastrain24']['value']:
            rain24=rain24+(self._attribute['lastrain24']['value'][rainTimeStamp]*self.__rainMM)
        return rain24
    def __calcRain1hmm(self):
        rain1h=0
        for rainTimeStamp in self._attribute['lastrain1h']['value']:
            rain1h=rain1h+(self._attribute['lastrain1h']['value'][rainTimeStamp]*self.__rainMM)
        return rain1h
         
if __name__ == "__main__":

    
    class logger(object):
        def write(self,arg):
            print arg['messages']
    loging=logger()
    arguente={'deviceID':{
                        "value":'ks300_rain@test.test'
                        },
             'typ':{
                        "value":'ks300_rain'
                        }
            }
    hmcDevice = device(arguente,loging)
    print("build hmc object")
    print("start thread")
    hmcDevice.setValue(906)
    while True:
        print("main wait 10 sec")
        sleep(10)    