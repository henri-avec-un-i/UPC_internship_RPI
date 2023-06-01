"""
TO CHANGE
Purpose: Acquire T and P data point at each trigger event, line by line. At the end of the experiment 
(after a specified time out delay), save the data array in a CSV file

Description:

TD : Wrap the whole script in a function, document well, add error handling ?

"""

#Library import
from __future__ import print_function
import RPi.GPIO as GPIO
import time
import csv
from sys import stdout
import numpy as np

#DAQ HATS Specific library
from T_P_acq_func import *
from daqhats import mcc128, OptionFlags, mcc134, HatIDs, HatError, TcTypes, AnalogInputMode, AnalogInputRange
from daqhats_utils import select_hat_device, tc_type_to_string, \
enum_mask_to_string, input_mode_to_string, input_range_to_string #This needs to be in the same folders as this script

### MCC HATS INITIALISATION
# Initialisation of MC128
channels_128=(0, 1)
address = select_hat_device(HatIDs.MCC_128)
hat_128 = mcc128(address)
input_mode = AnalogInputMode.SE
input_range = AnalogInputRange.BIP_5V
hat_128.a_in_mode_write(input_mode)
hat_128.a_in_range_write(input_range)

# Initialisation of MC134
channels_134=(0, 1)
address_134 = select_hat_device(HatIDs.MCC_134)
hat_134 = mcc134(address_134)
tc_type = TcTypes.TYPE_K
for channel in channels_134:
    hat_134.tc_type_write(channel, tc_type)



### GPIO pins set up
# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
trigger_pin = 17

# Set up the GPIO pin as an input with an initial high state
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# Initialisation of data_array
column_labels = ['Time', 'T1', 'T2', 'P1', 'P2'] # To modify as desired
data_array = []

# Initialisation of trigger event counter, used for timer
rising_edge_counter = 0



#Function executed at each trigger event
def trigger_callback(channel):
    """
    Callback function to be executed when the trigger input is detected.

    Args:
        channel (int): The GPIO channel number that triggered the callback.
        
        TD : Add timeout timer that exit the function and return the array and csv
    """
    
    '''
    if rising_edge_counter == 0:
        start_time = time.time()
        #Single read T and P, append the values to the data array, write time also

    
    else:
        current_time = time.time()
        relative_time = current_time - start_time
        #Single read T and P, append the values to the data array, write time also
        
    #Increment the rising edge counter, ie index of P and T measure
    rising_edge_counter += 1
    
    '''
    update_T_P_array(hat_134, hat_128, data_array, relative_time = None, channels_T=(0, 1), channels_P=(0, 1))
    print(data_array)
    print('Trigger detected')
    #print(get_current_T_P(hat_134, hat_128, channels_T=(0, 1), channels_P=(0, 1)))
    
    
    



# Add the event detection for the falling edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.RISING, callback=trigger_callback)


try:
    #While no trigger event, just display the pressure and temperature data, need to update function
    #in order to use LCD display 
    while True:
        #Function that display T and P data continuoulsy, Pressure alarm in bar
        #Need to pay attention to the refresh rate
        T_P_disp(channels_134=(0, 1), channels_128=(0, 1), delay_between_reads=0.001, alarm_on = False, pressure_alarm = 130)



except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
