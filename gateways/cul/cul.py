'''
Created on 05.12.2016

@author: uschoen
'''
__version__ = "1.6"
import threading
from time import localtime, strftime,sleep
from datetime import datetime
import socket
import serial
import sys


class server(threading.Thread):
    '''
    classdocs
    '''
    def __init__(self, parms,core,logger=False):
        threading.Thread.__init__(self)
        self.__core=core
        self.__logger=logger
        
        self.__config={}
        self.__config.update(self.__loadDefaultArgs())
        self.__config.update(parms)
        self.__config['host']=str(socket.gethostbyaddr(socket.gethostname())[0])
        self.__budget=0
        self.__pending_line=[]
        self.__read_queue=[]
        self.running=1
        self.__USBport=False
        self.__log("info","build  "+__name__+" instance")
    def run(self):
        try:
            self.__log("info","%s  start"%(__name__))
            self.__openUSB()
            self.__initCUL()        
            self.__readBudget()
            while self.running:
                if not self.__USBport:
                    self.__log("error","usb not open")
                    while self.__openUSB():
                        sleep(120)    
                    self.__initCUL()
                    self.__readBudget()
                read_line = self.__readResult()
                if read_line is not None:
                    if read_line.startswith("21  "):
                        self._pending_budget = int(read_line[3:].strip()) * 10 or 1
                        self.__log("info","get pending budget: %sms" % self._pending_budget)
                    elif read_line.startswith("K"):
                        self.__log("debug","get weather sensor response from CUL: '%s'" % read_line)
                        self.__decodeWeather(read_line.lstrip("K"))
                    elif read_line.startswith("F"):
                        self.__log("debug","get FS20 response from CUL: '%s'" % read_line)
                        self.__fs20Device(read_line.lstrip("F"))
                    else:
                        self.__log("warning","get unkown response from CUL: '%s'" % read_line)
                #self.__decodeWeather("17750049048AD3ED")
                #exit(0)
                #sleep(self.__config['sleeping']) 
            self.__log("warning",__name__+"  pause")
        except:
            self.__log("error",sys.exc_info())
    def __decodeWeather(self,msg):
        self.__log("debug","weather decode: %s leng %i" %(msg,len(msg)))
        split_msg=list(msg)
        if int(split_msg[1])==0:
            self.__log("debug","typ is AS3:%s"%(split_msg[1]))
        elif int(split_msg[1])==1:
            self.__log("debug","typ is AS2000, ASH2000, S2000, S2001A, S2001IA, ASH2200, S300IA:%s"%(split_msg[1]))
        elif int(split_msg[1])==2:
            self.__log("debug","typ is S2000R:%s"%(split_msg[1]))
        elif int(split_msg[1])==3:
            self.__log("debug","typ is S2000W:%s"%(split_msg[1]))
        elif int(split_msg[1])==4:
            self.__log("debug","typ is S2001I, S2001ID:%s"%(split_msg[1]))
        elif int(split_msg[1])==5:
            self.__log("debug","typ is S2500H:%s"%(split_msg[1]))
        elif int(split_msg[1])==6:
            self.__log("debug","typ is Pyrano (Strahlungsleistung):%s"%(split_msg[1]))
        elif int(split_msg[1])==7 and len(msg)==16:
            self.__log("debug","typ is ks300:%s"%(split_msg[1]))
            self.__ks300Device(msg)
        else:
            self.__log("info","typ is unkown:%s leng %i"%(split_msg[1],len(msg)))
    def __fs20Device(self,msg):
        self.__log("debug","fs20 get code %s"%(msg))
        deviceID="%s@%s.%s"%(msg[0:6],self.__config['gateway'],self.__config['host'])
        rssi=self.__rssi(int(msg[8:9],16))
        self.__log("debug","fs20 device code is %s"%(deviceID))
        if not deviceID in  self.__core.getAllDeviceId():
            self.__log("debug","new fs20 device: %s"%(deviceID))
            self.__core.addDevice(deviceID,"fs20")
        self.__core.setValue(deviceID,msg[6:8])
        self.__core.setDeviceAttributeValue(deviceID,"rssi",rssi)
    def __ks300Device(self,msg):
        self.__log("debug","ks300 get code %s"%(msg))
        if len(msg)<>16:
            self.__log("error", "inkorect message lenght: %s"%(len(msg)))
            return
        splitMsg=list(msg)
        rssi=self.__rssi(int(splitMsg[14]+splitMsg[15],16))

        ''' tmperatur '''
        deviceID="ks300_temperatur@%s.%s"%(self.__config['gateway'],self.__config['host'])
        if not deviceID in self.__core.getAllDeviceId():
            self.__core.addDevice(deviceID,"ks300_temperatur")
        value=float(splitMsg[5]+splitMsg[2]+"."+splitMsg[3])
        if splitMsg[0] >="8":
            value=value*(-1)
        self.__core.setValue(deviceID,value)
        self.__core.setDeviceAttributeValue(deviceID,"rssi",rssi)
        ''' humidity'''
        deviceID="ks300_humidity@%s.%s"%(self.__config['gateway'],self.__config['host'])
        if not deviceID in self.__core.getAllDeviceId():
            self.__core.addDevice(deviceID,"ks300_humidity")
        value=int(splitMsg[7]+splitMsg[4])
        self.__core.setValue(deviceID,value)
        self.__core.setDeviceAttributeValue(deviceID,"rssi",rssi)
        ''' wind '''
        deviceID="ks300_wind@%s.%s"%(self.__config['gateway'],self.__config['host'])
        if not deviceID in self.__core.getAllDeviceId():
            self.__core.addDevice(deviceID,"ks300_wind")
        value=int(splitMsg[8]+splitMsg[9]+splitMsg[6])
        self.__core.setValue(deviceID,value)
        self.__core.setDeviceAttributeValue(deviceID,"rssi",rssi)
        ''' windchill '''
        deviceID="ks300_windchill@%s.%s"%(self.__config['gateway'],self.__config['host'])
        if not deviceID in self.__core.getAllDeviceId():
            self.__core.addDevice(deviceID,"ks300_windchill")
        value=int(splitMsg[8]+splitMsg[9]+splitMsg[6])
        self.__core.setValue(deviceID,value)
        self.__core.setDeviceAttributeValue(deviceID,"rssi",rssi)
        ''' rain '''
        deviceID="ks300_rain@%s.%s"%(self.__config['gateway'],self.__config['host'])
        if not deviceID in self.__core.getAllDeviceId():
            self.__core.addDevice(deviceID,"ks300_rain")
        value=int(splitMsg[13]+splitMsg[10]+splitMsg[11],16)
        self.__core.setValue(deviceID,value)
        self.__core.setDeviceAttributeValue(deviceID,"rssi",rssi)
    def __loadDefaultArgs(self):
        args={
              'usbport':"/dev/ttyUSB0",
              'baudrate':"9600",
              'timeout':1,
              'sleeping':0
              }
        return args
    def __rssi(self,RAWvalue):
        '''
        calculate  RSSI Value
        '''
        rssi=RAWvalue
        if rssi>=128:
            rssi=((rssi-256)/2-74)
        else:
            rssi=rssi/2-74
        return rssi
    def __readBudget(self):
        self.__sendCommand("X")
    def __openUSB(self):
        if not self.__USBport:
            try:
                self.__log("info","open serial, port:%s baud:%s timeout:%s"%(self.__config['usbport'],self.__config['baudrate'],self.__config['timeout']))
                self.__USBport=serial.Serial(
                              port='/dev/ttyACM0',
                              baudrate = self.__config['baudrate'],
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              bytesize=serial.EIGHTBITS,
                              timeout=self.__config['timeout']
                            )
                return True
            except:
                
                self.__log("warning","can not open serial, port:%s baud:%s timeout:%s"%(self.__config['usbport'],self.__config['baudrate'],self.__config['timeout']))
                self.__USBport=False
                return False
        return True
    def __closeUSB(self):
        self.__log("info","close serial, port:"+str(self.__config['usbport'])+" baud:"+str(self.__config['baudrate'])+" timeout:"+str(timeout = self.__config['timeout']))
        self.__USBport.close()
    def __initCUL(self):
        '''
        init command for cul stick
        '''
        self.__log("info","initCUL")
        self.__sendCommand("X21")
        sleep(0.3)        
    def __sendCommand(self, command):
        self.__log("info","send command:%s"%(command))
        if not self.__USBport:
            self.__log("error","usb not open")
            while self.__openUSB():
                sleep(120)    
            self.__initCUL()
            self.__readBudget()
        if command.startswith("Zs"):
            self.__budget = 0
        self.__USBport.write(command + "\r\n")
    def __readResult(self):
        while self.__USBport.inWaiting():
            self.__pending_line.append(self.__USBport.read(1))
            if self.__pending_line[-1] == "\n":
                completed_line = "".join(self.__pending_line[:-2])
                self.__log("debug","received: %s" % completed_line)
                self.__pending_line = []
                if completed_line.startswith("Z"):
                    self.__read_queue.put(completed_line)
                else:
                    return completed_line
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
    args={
              'usbport':"/dev/ttyUSB0",
              'baudrate':"9600",
              'timeout':None,
              'sleeping':1
              }
    loging=logger()
    threadInstance = server(args,False,loging)
    print("build thread")
    threadInstance.daemon = True
    threadInstance.start()
    print("start thread")
    while True:
        print("main wait 10 sec")
        sleep(10)    