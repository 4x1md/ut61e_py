"""
Created on 12.2.2019

@author: https://github.com/Bo-M/
         
@note: The script uses UT61E class from 4x1md(https://github.com/4x1md/ut61e_py) which to parser data recorded from UNI-T UT61E 
	   using serial interface and displays it in human readable form. If you log your data using arduino or some other µP than 
	   you can use this example to parse data to human readable format.
"""

from __future__ import print_function
from ut61e import UT61E
import sys
import time
import datetime
from serial import SerialException

SLEEP_TIME = 0.25

if __name__ == '__main__':
    print("Starting UT61E parser...")
    
    
    dmm = UT61E()
	
    data = '400363;60080' #example how the data should Lookalike
    meas = dmm.get_readable(offlineData = data, disp_norm_val= True)
    print()
    print(datetime.datetime.now())
    print(meas)
    
    time.sleep(SLEEP_TIME)
        

