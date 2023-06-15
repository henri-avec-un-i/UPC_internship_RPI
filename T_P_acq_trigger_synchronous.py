from __future__ import print_function #Must be at the beginning of the file for some reasons

################################################

"""

Description:

TD : Wrap the whole script in a function, document well, add error handling ?

TO IMPLEMENT LATER WITH THREADING
#Time after which the acquisition stops and the data is saved as a CSV, in seconds
timeout_delay = 5

"""
################################################

"""
Imports
"""

#General purpose library
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
enum_mask_to_string, input_mode_to_string, input_range_to_string 

#daqhats_utils needs to be in the same folders as this script

################################################

"""
Hardware initialisation
"""

### MCC HATS INITIALISATION
# Initialisation of MC128
channels_128=(0, 1) #Hardware channel on which the sensors are connected to the MC 128 board. Check MCC Documentation for references
address = select_hat_device(HatIDs.MCC_128) #Initialisation of HAT adress
hat_128 = mcc128(address) #Creation of board object of class mcc128
input_mode = AnalogInputMode.SE #Selection of input mode between Single ended and Differential mode for Analog read of the sensor input. Check MCC Documentation for references
input_range = AnalogInputRange.BIP_5V # Selection of analog input voltage range. For current pressure sensor (RS: 797-4986), range is 0-5V
hat_128.a_in_mode_write(input_mode) #Write the input mode to the HAT board
hat_128.a_in_range_write(input_range) #Write the input range to the HAT board

channels_T = channels_128 #MCC 128 channels are used for pressure measurment

# Initialisation of MC134
channels_134=(0, 1) #Hardware channel on which the sensors are connected to the MC 134 board. Check MCC Documentation for references
address_134 = select_hat_device(HatIDs.MCC_134) #Initialisation of HAT adress
hat_134 = mcc134(address_134) #Creation of board object of class mcc134
tc_type = TcTypes.TYPE_K #Selection of thermocouple type for MCC 134. Current sensor (RS: 847-9665) are type K
for chan in channels_134: # Write the Thermocouple type to the channels of MC 134
    hat_134.tc_type_write(chan, tc_type)
    
channels_P = channels_134 #MCC 134 channels are used for temperature measurment

### GPIO pins set up
# Set the GPIO mode to BCM indexing (vs Physical indexing). Check Raspberry Pi pinout for references
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin indexes
trigger_pin = 17 #Trigger pin index. Syncronisation signal from syncroniser box is received on this pin.


# Set up the GPIO pin as an input/output state as well as default state
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #trigger pin defined as input and by pulled down by default to avoid floating state when no input is given


### LCD set up
#Initialisation of the lcd object from RPLCD library, to modify according to LCD current pinout
lcd = CharLCD(pin_rs=19, pin_e=6, pins_data=[23, 24, 22, 27],
			  numbering_mode=GPIO.BCM,
			  cols=20, rows=4, dotsize=8,
			  charmap='A02',
			  auto_linebreaks=True)


################################################

"""
Data stucture initialisation
"""

### Initialisation of data_array
header = ['Index', 'Time', 'T1', 'T2', 'P1', 'P2'] # To modify as desired
filename = 'data_single_read_trigger.csv'
data_array = []

### Definition of script constants
T_hot_wall = 50 # Hot wall temperature, to specify, in Celcius, to measure later directly on the Peltier module
pressure_alarm = 130 #Pressure alarm threshold for alarm and system shutdown

#Initialisation of rising_edge_counter, ie. number of trigger signal received, indicate the index of the current measure
rising_edge_counter = 0


################################################

"""
Main script logic
"""

#Function executed at each trigger event
def trigger_callback(trigger_pin):
    """
    Callback function to be executed when the trigger input is detected.

    Args:
        channel (int): The GPIO channel number that triggered the callback.
        
    """
    
    #I need to set this variables as global because I want to update data_array and rising_edge_counter through this trigger_callback function
    global data_array
    global start_time
    global rising_edge_counter
    
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
        T_P_disp(lcd, T_hot_wall, channels_134=(0, 1), channels_128=(0, 1), delay_between_reads=0.5, alarm_on = False, pressure_alarm = 130, terminal_output = True, lcd_output = True)



except KeyboardInterrupt:
    # Save data array as a csv, print it if you want and clean data_array
    save_data_to_csv(data_array, header, filename)
    data_array = []    
    print("Exiting...")
    GPIO.cleanup()
