'''
Created on 05.12.2016

@author: uschoen
'''
from hmcDevices import defaultDevice
from time import sleep

__version__="1.9"

class device(defaultDevice):
    '''
    classdocs
    '''
    def _name_(self):
        return "ks300_windchill"
    '''
     set value 
     public function
    '''
    def setValue(self,Value):
        windchill=self.__WeatherWindChill(Value)
        self._log("debug","set sensor data to %s"%(windchill))
        if windchill==self._attribute['value']['value']:
            self._onrefresh_event()
        else:
            self._attribute['value']['value']=windchill
            self._onrefresh_event()
            self._onchange_event()
    '''
    calculate windchill
    '''    
    def __WeatherWindChill(self,wind): 
        self._log("debug","calc windchill, wind is:%s"%(wind))  
        if wind == 0:
            return "0"
        elif wind in range(1,6):
            return 1
        elif wind in range(6,12):
            return 2
        elif wind in range(12,20):
            return 3
        elif wind in range(20,29):
            return 4
        elif wind in range(29,39):
            return 5
        elif wind in range(39,50):
            return 6
        elif wind in range(50,62):
            return 7
        elif wind in range(62,75):
            return 8
        elif wind in range(75,89):
            return 9
        elif wind in range(89,103):
            return 10
        elif wind in range(103,117):
            return 11
        elif wind >116:
            return 12
        else:
            self._log("error","wind  can not macht from 0 - >116 ")  
            return "0" 
if __name__ == "__main__":

    
    class logger(object):
        def write(self,arg):
            print arg['messages']
    loging=logger()
    hmcDevice = device(loging)
    print("build hmc object")
    print("start thread")
    hmcDevice.setValue(90)
    while True:
        print("main wait 10 sec")
        sleep(10)    