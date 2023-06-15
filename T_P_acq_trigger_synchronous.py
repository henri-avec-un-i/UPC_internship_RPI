from __future__ import print_function #Must be at the beginning of the file for some reasons

################################################

"""

Description:

This script performs data acquisition and logging of temperature and pressure measurements triggered by an external input signal. It initializes the hardware components, sets up the GPIO pins, and defines the data structures and constants used in the script. The main logic of the script includes a callback function that is executed when the trigger input is detected, updating the data array with a new line for each trigger event. The script continuously displays temperature and pressure data on an LCD screen while waiting for trigger events. If a keyboard interrupt signal is received, the data array is saved as a CSV file, and the script terminates by cleaning up the GPIO pins.

Note: The code contains placeholders for implementing threading and a timeout delay for data acquisition, which can be implemented later.

Imported Libraries:
- RPi.GPIO: Library for controlling GPIO pins on Raspberry Pi.
- time: Library for time-related functions.
- csv: Library for CSV file handling.
- sys: Library for system-specific parameters and functions.
- numpy: Library for array manipulation.
- RPLCD: Library for controlling LCD displays.
- T_P_acq_func: Custom library for temperature and pressure acquisition functions.
- daqhats: Library for interacting with MCC DAQ HATs.
- daqhats_utils: Library for utility functions related to MCC DAQ HATs.

Hardware Initialization:
- MCC HATS: Initialization of MCC 128 and MCC 134 DAQ HATs, setting input modes and ranges.
- GPIO Pins: Setting up the GPIO pins on Raspberry Pi for trigger input.
- LCD Setup: Initializing the LCD object with pin configurations.

Data Structure Initialization:
- data_array: Initializing an empty array to store temperature and pressure measurements.
- header: A list containing column names for the data array.
- filename: Name of the CSV file to save the data.
- T_hot_wall: Hot wall temperature in Celsius.
- pressure_alarm: Threshold value for pressure alarm and system shutdown.
- rising_edge_counter: Counter for the number of trigger events.

Main Script Logic:
- data_array_update: Callback function executed when the trigger input is detected. It updates the data array with a new line containing the index, relative time, and current temperature and pressure measurements.
- GPIO event detection: Adding event detection for the rising edge of the trigger input, calling the data_array_update function.
- Main loop: Continuously displays temperature and pressure data on the LCD screen while waiting for trigger events.
- KeyboardInterrupt handling: If a keyboard interrupt signal is received, the data array is saved as a CSV file, and the script exits after cleaning up the GPIO pins.
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
T_hot_wall = 50 # Hot wall temperature in Celcius, to specify, in Celcius, to measure later directly on the Peltier module
pressure_alarm = 130 #Pressure alarm threshold in bar for alarm and system shutdown

#Initialisation of rising_edge_counter, ie. number of trigger signal received, indicate the index of the current measure
rising_edge_counter = 0


################################################

"""
Main script logic
"""

#Function executed at each trigger event
def data_array_update(trigger_pin):
    """
    Callback function to be executed when the trigger input is detected. Updates the data array with a new line each time it is called. 
    

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

# Add the event detection for the rising edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.RISING, callback=data_array_update)


try:
    #While no trigger event, just display the pressure and temperature data
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
