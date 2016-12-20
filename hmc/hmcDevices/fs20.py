'''
Created on 05.12.2016

@author: uschoen
'''
from hmcDevices import defaultDevice
__version__="1.9"

class device(defaultDevice):
    '''
    classdocs
    '''
    def _name_(self):
        return "fs20"   