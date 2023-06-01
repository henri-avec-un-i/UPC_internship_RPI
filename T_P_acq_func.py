from __future__ import print_function
import csv
from time import sleep
from sys import stdout
import numpy as np
from datetime import datetime
import RPi.GPIO as GPIO


from daqhats import mcc128, OptionFlags, mcc134, HatIDs, HatError, TcTypes, AnalogInputMode, AnalogInputRange
from daqhats_utils import select_hat_device, tc_type_to_string, \
enum_mask_to_string, input_mode_to_string, input_range_to_string #This needs to be in the same folders as this script

"""
Purpose:
    Contain the different functions used for P and T data acquisition.

"""


# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins number
alarm_pin = 27
system_shutdown_pin = 22

# Set up the GPIO pins as an output
GPIO.setup(alarm_pin, GPIO.OUT)
GPIO.setup(system_shutdown_pin, GPIO.OUT)



def sound_alarm():
    """
    Rings a sound alarm, to complete

    Args: to complete

    Returns: to complete

    """
    #set alarm digital output pin to high
    GPIO.output(alarm_pin, GPIO.HIGH)

def no_sound_alarm():
    """
    stop the sound alarm, to complete

    Args: to complete

    Returns: to complete

    """
    #set alarm digital output pin to low
    GPIO.output(alarm_pin, GPIO.LOW)


def system_shutdown():
    """
    Shutdowns the system (shutdown valves,... to complete), to complete

    Args: to complete

    Returns: to complete

    """
    #set stop system digital output pin to high
    GPIO.output(system_shutdown_pin, GPIO.HIGH)


def no_system_shutdown():
    """
    Stops the system shutdown (shutdown valves,... to complete), to complete

    Args: to complete

    Returns: to complete

    """
    #set stop system digital output pin to low
    GPIO.output(system_shutdown_pin, GPIO.LOW)





def volt_to_bar(volt_value, slope=50, offset=0):
    """
    Converts a voltage value to a bar value using linear conversion.

    Args:
        volt_value (float): The voltage value to convert.
        slope (float, optional): The slope coefficient for the linear conversion. Defaults to 50.
        offset (float, optional): The offset coefficient for the linear conversion. Defaults to 0.

    Returns:
        float: The bar value converted from the voltage value.
    """
    # Apply linear conversion formula: bar_value = volt_value * slope + offset
    bar_value = volt_value * slope + offset

    return bar_value



def T_P_acq_csv(channels_134=(0, 1), channels_128=(0, 1), acq_frequency=1, N_measures=10, terminal_output=True,
                data_filename="data.csv", alarm_on = True, pressure_alarm = 130):
    """
    Acquires Pressure and Temperature data before and after microchip and writes it to a CSV file.

    Args:
        channels_134 (tuple, optional): Sensors channels on MC134. Defaults to (0, 1).
        channels_128 (tuple, optional): Sensors channels on MC128. Defaults to (0, 1).
        acq_frequency (int, optional): Acquisition frequency in Hz. Defaults to 1.
        N_measures (int, optional): Number of measures. Defaults to 10.
        terminal_output (bool, optional): Whether to display terminal output. Defaults to True.
        data_filename (str, optional): Name of the data CSV file. Defaults to "data.csv".
        alarm_on (bool, optional):  Wheter to activate the safety alarm. Default to True
        pressure_alarm (float, optional): Pressure alarm threshold. Default to 130 bars
    """
    import datetime

    try:
        # Initialisation of MC128
        address = select_hat_device(HatIDs.MCC_128)
        hat_128 = mcc128(address)
        input_mode = AnalogInputMode.SE
        input_range = AnalogInputRange.BIP_5V
        hat_128.a_in_mode_write(input_mode)
        hat_128.a_in_range_write(input_range)

        # Initialisation of MC134
        address_134 = select_hat_device(HatIDs.MCC_134)
        hat_134 = mcc134(address_134)
        tc_type = TcTypes.TYPE_K

        # Initialisation of P and T data arrays
        T_array = np.zeros((N_measures, len(channels_134)))
        P_array = np.zeros((N_measures, len(channels_128)))
        
        #Date initialisation for cvs header
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        # delay_between_reads corresponds to the sleep time of the Pi between each mesures 
        delay_between_reads = 1 / acq_frequency
        
        #csv file initialisation
        with open(data_filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            
            #Writes header
            writer.writerow(["Date and time", formatted_datetime, "Number of measures: ", N_measures,
                             "Acquisition frequency: ", acq_frequency, "Hz"])
            writer.writerow(["N_measure", "Pressure 1", "Temperature 1", "Pressure 2", "Temperature 2"])

            if terminal_output:
                print('\nAcquiring data ... Press Ctrl-C to abort')
                print('\nNumber of measures:', N_measures, 'Acquisition frequency:', acq_frequency, 'Hz')
                print('\nDate and time:', formatted_datetime)
                print('\n  Sample', end='')
                for channel in channels_128:
                    print('     Channel Temperature', channel, end='')
                for channel in channels_134:
                    print('     Channel Pressure', channel, end='')
                print('')

            #Initialisation of samples count, displayed in the first column of the csv fils
            samples_per_channel = 0
            
            # Data acquisition
            for i in range(N_measures):
                # Set the status of the alarm and shutdown routine to off
                no_sound_alarm()
                no_system_shutdown()
                
                #Updates the sample count for each new measurent
                samples_per_channel += 1
                if terminal_output:
                    print('\r{:8d}'.format(samples_per_channel), end='')
                
                # Temperature measurement
                for channel in channels_134:
                    hat_134.tc_type_write(channel, tc_type)
                    value_T = hat_134.t_in_read(channel)
                    T_array[i, channel] = value_T

                    if terminal_output:
                        if value_T == mcc134.OPEN_TC_VALUE:
                            print('     Open     ', end='')
                        elif value_T == mcc134.OVERRANGE_TC_VALUE:
                            print('     OverRange', end='')
                        elif value_T == mcc134.COMMON_MODE_TC_VALUE:
                            print('   Common Mode', end='')
                        else:
                            print('{:12.2f} C'.format(value_T), end='')

                # Pressure measurement
                for channel in channels_128:
                    value_P_volt = hat_128.a_in_read(channel)
                    value_P_bar = volt_to_bar(value_P_volt)
                    P_array[i, channel] = value_P_bar
                
                # Pressure alarm check    
                if alarm_on:
                    if value_P_bar > pressure_alarm:
                        #call pressure_alarm function
                        sound_alarm()
                        #call system_shutdown function
                        system_shutdown()
                        
                        print('Warning : Pressure above ', pressure_alarm,' bar')
                   
                    else:
                        no_sound_alarm()
                        no_system_shutdown()
                        
                    if terminal_output:
                        print('{:12.2f} bar'.format(value_P_bar), end='')

                stdout.flush()
                # Delay between reads
                sleep(delay_between_reads)
                
                # Writes the row of data to the csv file
                row = [i, P_array[i, 0], T_array[i, 0], P_array[i, 1], T_array[i, 1]]
                writer.writerow(row)

    except (HatError, ValueError) as error:
        print('\n', error)






def T_P_disp(channels_134=(0, 1), channels_128=(0, 1), delay_between_reads=0.1, alarm_on = True, pressure_alarm = 150):
    """
    Displays real-time Temperature and Pressure data from sensors on MC134 and MC128.

    Args:
        channels_134 (tuple, optional): Sensors channels on MC134. Defaults to (0, 1).
        channels_128 (tuple, optional): Sensors channels on MC128. Defaults to (0, 1).
        delay_between_reads (float, optional): Delay between sensor readings in seconds. Defaults to 0.1.
        alarm_on (bool, optional):  Wheter to activate the safety alarm. Default to True
        pressure_alarm (float, optional): Pressure alarm threshold. Default to 130 bars
    """
    import datetime

    try:
        # Initialisation of MC128
        address = select_hat_device(HatIDs.MCC_128)
        hat_128 = mcc128(address)
        input_mode = AnalogInputMode.SE
        input_range = AnalogInputRange.BIP_5V
        hat_128.a_in_mode_write(input_mode)
        hat_128.a_in_range_write(input_range)

        # Initialisation of MC134
        address_134 = select_hat_device(HatIDs.MCC_134)
        hat_134 = mcc134(address_134)
        tc_type = TcTypes.TYPE_K
        
        #Date initialisation for cvs header
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Writes the thermocouple type in MC134 memory
        for channel in channels_134:
            hat_134.tc_type_write(channel, tc_type)

        # Display the header row for the data table.
        for channel in channels_128:
            print('     Channel Temperature', channel, end='')
        for channel in channels_134:
            print('     Channel Pressure', channel, end='')
        print('')

        while True:
            no_sound_alarm()
            no_system_shutdown()
            
            # Temperature measurement
            for channel in channels_134:
                value_T = hat_134.t_in_read(channel)

                if value_T == mcc134.OPEN_TC_VALUE:
                    print('     Open     ', end='')
                elif value_T == mcc134.OVERRANGE_TC_VALUE:
                    print('     OverRange', end='')
                elif value_T == mcc134.COMMON_MODE_TC_VALUE:
                    print('   Common Mode', end='')
                else:
                    print('{:12.2f} C'.format(value_T), end='')
                    
            # Pressure measurement
            for channel in channels_128:
                value_P_volt = hat_128.a_in_read(channel)
                value_P_bar = volt_to_bar(value_P_volt)
                
                # Pressure alarm check 
                if alarm_on:
                    if value_P_bar > pressure_alarm:
                        #call pressure_alarm function
                        sound_alarm()
                        #call system_shutdown function
                        system_shutdown()
                        print('Warning : Pressure above ', pressure_alarm,' bar')

                      
                #This is here in order to print continuously T and P values over the same line
                if channel == channels_128[-1]:
                    print('{:12.2f} bar'.format(value_P_bar), end='\r')
                else:
                    print('{:12.2f} bar'.format(value_P_bar), end='')

            stdout.flush()
            sleep(delay_between_reads)

    except (HatError, ValueError) as error:
        print('\n', error)
        GPIO.cleanup()


        
def csv_data_reader(file_name = "data.csv", terminal_output = False):
    
    """
    Reads data from a data CSV file and returns acquisition parameters, column headers, and data as arrays.

    Args:
        file_name (str): The name of the CSV file to read. Default is "data.csv".
        terminal_output (bool): Flag to determine whether to print the acquired data to the terminal.
                               Default is False.

    Returns:
        tuple: A tuple containing the acquisition parameters, column headers, and data as arrays.

    """
    
    # Specify the path to the CSV file
    csv_file = file_name

    # Initialize empty arrays for acquisition parameters, headers, and data
    acquisition_params = []
    column_headers = []
    data = []

    # Read the CSV file
    with open(csv_file, "r") as file:
        reader = csv.reader(file)

        # Extract the acquisition parameters from the first line
        acquisition_params = next(reader)

        # Extract the headers from the second line
        column_headers = next(reader)

        # Read the rest of the lines as data
        data = list(reader)
    
    if terminal_output:
        # Print the arrays if terminal_output == True
        print("Acquisition Parameters:", acquisition_params)
        print("Column Headers:", column_headers)
        print("Data:")
        for row in data:
            print(row)

    return acquisition_params, column_headers, np.array(data)




def get_current_T_P(hat_134, hat_128, channels_T=(0, 1), channels_P=(0, 1)):
    """
    TO CHANGE
    Appends to the data array new values of T and P as well as the time of measurement, need to use list of
    lists in order to be able to append new lines without creating new arrays each times (not possible in np<)
    
    channels_T = channel MCC 134
    channels_P = channel MCC 128

    Args:
    
    value_P_volt = hat_128.a_in_read(channel)
                value_P_bar = volt_to_bar(value_P_volt)
        
    Output: T_values (list), P_values (list)
    """
    
    T_values = []
    P_values = []
    
    for channel in channels_T:
        T_values.append(hat_134.t_in_read(channel))
    
    for channel in channels_P:
        P_values.append(volt_to_bar(hat_128.a_in_read(channel)))
    
    new_T_P_values = T_values + P_values
    
    return new_T_P_values




def update_T_P_array(hat_134, hat_128, data_array, relative_time, channels_T=(0, 1), channels_P=(0, 1)):
    
    """
    TO CHANGE
    Appends to the data array new values of T and P as well as the time of measurement, need to use list of
    lists in order to be able to append new lines without creating new arrays each times (not possible in np)
    
    Args:
        
    Output: Updated data array
    """
    
    new_row = get_current_T_P(hat_134, hat_128, channels_T=(0, 1), channels_P=(0, 1)) + [relative_time]
    
    #If the array is empty (first measure), then return the first measure in a appendable array
    if data_array == []:
        data_array = [new_row]
        return data_array #Check if format is ok
        
    else:
        data_array.append(new_row)
        return data_array


































