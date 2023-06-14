"""

Description:

TD : Wrap the whole script in a function, document well, add error handling ?

TO IMPLEMENT LATER WITH THREADING
#Time after which the acquisition stops and the data is saved as a CSV, in seconds
timeout_delay = 5

"""

#Library import
from __future__ import print_function
import RPi.GPIO as GPIO
import time
import csv
from sys import stdout
import numpy as np
from RPLCD import CharLCD, cleared, cursor


#DAQ HATS Specific library
from T_P_acq_func import *
from daqhats import mcc128, OptionFlags, mcc134, HatIDs, HatError, TcTypes, AnalogInputMode, AnalogInputRange
from daqhats_utils import select_hat_device, tc_type_to_string, \
enum_mask_to_string, input_mode_to_string, input_range_to_string #This needs to be in the same folders as this script

"""

Docstring here

"""


### MCC HATS INITIALISATION
# Initialisation of MC128
channels_128=(0, 1)
address = select_hat_device(HatIDs.MCC_128)
hat_128 = mcc128(address)
input_mode = AnalogInputMode.SE
input_range = AnalogInputRange.BIP_5V
hat_128.a_in_mode_write(input_mode)
hat_128.a_in_range_write(input_range)
channels_T = channels_128

# Initialisation of MC134
channels_134=(0, 1)
address_134 = select_hat_device(HatIDs.MCC_134)
hat_134 = mcc134(address_134)
tc_type = TcTypes.TYPE_K
for chan in channels_134:
    hat_134.tc_type_write(chan, tc_type)
channels_P = channels_134

### GPIO pins set up
# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
trigger_pin = 17


# Set up the GPIO pin as an input with an initial high state
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)




#Initialisation of the lcd object from RPLCD library, to modify according to LCD current pinout
lcd = CharLCD(pin_rs=19, pin_e=6, pins_data=[23, 24, 22, 27],
			  numbering_mode=GPIO.BCM,
			  cols=20, rows=4, dotsize=8,
			  charmap='A02',
			  auto_linebreaks=True)


# Initialisation of data_array
header = ['Index', 'Time', 'T1', 'T2', 'P1', 'P2'] # To modify as desired
filename = 'data_single_read_trigger.csv'
data_array = []

T_hot = 50 # Hot wall temperature, to specify, in Celcius 

pressure_alarm = 130 #Pressure alarm threshold for alarm and system shutdown

#Initialisation of rising_edge_counter, indicate the index of the current measure
rising_edge_counter = 0



#Function executed at each trigger event
def trigger_callback(trigger_pin):
    """
    Callback function to be executed when the trigger input is detected.

    Args:
        channel (int): The GPIO channel number that triggered the callback.
        
    """
    
    global data_array
    global start_time
    global rising_edge_counter
    global timeout_delay
    
    #Timer start at first measure, ie first rising edge
    if rising_edge_counter == 0:
        start_time = time.time()
    
    relative_time = time.time() - start_time
    
    # Retrieve the current temperature and pressure measurement values
    new_row = [rising_edge_counter] + [relative_time] + get_current_T_P(hat_134, hat_128, pressure_alarm, channels_T, channels_P)
    
    # If the array is empty (first measurement), create a new array with the first measurement
    if data_array == []:
        data_array = [new_row]
    else:
        data_array.append(new_row)
    
    
    rising_edge_counter += 1
    
    #print(rising_edge_counter)


# Add the event detection for the falling edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.RISING, callback=trigger_callback)


try:
    #While no trigger event, just display the pressure and temperature data, need to update function
    #in order to use LCD display
    while True:
        #Function that display T and P data continuoulsy, Pressure alarm in bar
        #Need to pay attention to the refresh rate COMPARED TO acquisition rate
        T_P_disp(lcd, T_hot, channels_134=(0, 1), channels_128=(0, 1), delay_between_reads=0.5, alarm_on = False, pressure_alarm = 130, terminal_output = True, lcd_output = True)



except KeyboardInterrupt:
    # Save data array as a csv, print it if you want and clean data_array
    save_data_to_csv(data_array, header, filename)
    data_array = []    
    print("Exiting...")
    GPIO.cleanup()
