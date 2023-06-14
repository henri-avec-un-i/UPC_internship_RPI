#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
    MCC 134 Functions Demonstrated:
        mcc134.t_in_read

    Purpose:
        Read a single data value for each channel in a loop.

    Description:
        This example demonstrates acquiring data using a software timed loop
        to read a single value from each selected channel on each iteration
        of the loop.
"""
from __future__ import print_function
from time import sleep
from sys import stdout
from daqhats import mcc134, HatIDs, HatError, TcTypes
from daqhats_utils import select_hat_device, tc_type_to_string


import numpy as np



tc_type = TcTypes.TYPE_K   # change this to the desired thermocouple type
delay_between_reads = 0.5  # #To specify, Seconds
N_measures = 10 #To specify
channels = (0, 1) #To specify
T_array = np.zeros((N_measures,len(channels))) # List of temperatures for both sensors in Celsius



try:
    # Get an instance of the selected hat device object.
    address = select_hat_device(HatIDs.MCC_134)
    hat = mcc134(address)

    for channel in channels:
        hat.tc_type_write(channel, tc_type)
    
    for i in range(N_measures):
        # Read a single value from each selected channel.
        for channel in channels:
            value = hat.t_in_read(channel)
            T_array[i,channel] = value
            print(value, '', i)
            
        # Wait the specified interval between reads.
        sleep(delay_between_reads)
        
    print(T_array)


except (HatError, ValueError) as error:
    print('\n', error)

