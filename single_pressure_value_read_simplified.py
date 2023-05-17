#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
    
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
from daqhats import mcc128, OptionFlags, HatIDs, HatError, AnalogInputMode, AnalogInputRange
from daqhats_utils import select_hat_device, enum_mask_to_string, input_mode_to_string, input_range_to_string

import numpy as np


#Input parameters
input_mode = AnalogInputMode.SE
input_range = AnalogInputRange.BIP_5V

# Get an instance of the selected hat device object.
address = select_hat_device(HatIDs.MCC_128)
hat_128 = mcc128(address)

#Configuration of hat
hat_128.a_in_mode_write(input_mode)
hat_128.a_in_range_write(input_range)


#Parameters of acquisition
delay_between_reads = 0.5  # #To specify, Seconds
N_measures = 100 #To specify
channels = (0, 1) #To specify
P_array = np.zeros((N_measures,len(channels))) # List of pressures for both sensors in bars, don't forget to convert from volt to bars !!

#Function to convert sensor volt input to bar using linear conversion, 
#coefficients are to be adjusted with a calibration step, also linearity
#between volts and bar value is to be checked
def Volt_to_bar(volt_value, slope = 50, offset = 0):
    bar_value = volt_value*slope + offset
    return bar_value

try:
    
    print('Pressure values of channel 0 and 1 in bars')
    print('0    1')
    for i in range(N_measures):
    # Read a single value from each selected channel.
        for channel in channels:
            volt_value = hat_128.a_in_read(channel)
            P_array[i,channel] = Volt_to_bar(volt_value)
        print(P_array[i,:], '', i)
        
        # Wait the specified interval between reads.
        sleep(delay_between_reads)

    print(P_array)



except (HatError, ValueError) as error:
    print('\n', error)



