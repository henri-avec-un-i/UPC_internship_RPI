
# Acquiring the T and P data
from __future__ import print_function
from time import sleep
from sys import stdout
from daqhats import mcc128, OptionFlags, mcc134, HatIDs, HatError, TcTypes, AnalogInputMode, AnalogInputRange
from daqhats_utils import select_hat_device, tc_type_to_string, \
enum_mask_to_string, input_mode_to_string, input_range_to_string #This needs to be in the same folders as this script

import numpy as np



#Function to convert sensor volt input to bar using linear conversion, 
#coefficients are to be adjusted with a calibration step, also linearity
#between volts and bar value is to be checked
def Volt_to_bar(volt_value, slope = 50, offset = 0):
    bar_value = volt_value*slope + offset
    return bar_value


def T_P_acq_csv(channels_134 = (0, 1), channels_128 = (0, 1), acq_frequency = 1, N_measures = 10, terminal_output = True, data_filename = "data.csv"):
    '''
    Description :
    Inputs : channels_134 = sensors channel on MC134, channels_128 = sensors channel on MC128, 
    Outputs :
    
    '''
    
    #Returns a csv data file with Pressure and Temperature data before and after microchip
    #acq_frequency in Herz, max acq_frequency for Temperature is 1 Hz (cf. manufacturer datasheet)
    #Set terminal_output to false if you don't want terminal output
    
    import datetime #Warning : Time and date set by Rasperry Pi internal clock, out of sync if powered down
    
    # Initialisation of MC128
    ## Input parameters
    input_mode = AnalogInputMode.SE
    input_range = AnalogInputRange.BIP_5V

    ## Get an instance of the selected hat device object.
    address = select_hat_device(HatIDs.MCC_128)
    hat_128 = mcc128(address)

    ## Configuration of hat
    hat_128.a_in_mode_write(input_mode)
    hat_128.a_in_range_write(input_range)

    #Initialisation of MC134
    address_134 = select_hat_device(HatIDs.MCC_134)
    hat_134 = mcc134(address_134)
    tc_type = TcTypes.TYPE_K   # change this to the desired thermocouple type
    
    #Initialisation of P and T data arrays
    T_array = np.zeros((N_measures,len(channels_134))) # List of temperatures of sensors in Celsius
    P_array = np.zeros((N_measures,len(channels_128))) # List of pressures of sensors in bars
        
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    delay_between_reads = 1/acq_frequency # #To specify, in seconds

    ##Get Temperature data and pressure data
    try:        
        
        for channel in channels_134:
            hat_134.tc_type_write(channel, tc_type)
            
        if terminal_output == True:    
            print('\nAcquiring data ... Press Ctrl-C to abort')
            print('\nNumber of measures : ', N_measures,'Acquisition frequency : ', acq_frequency,'Hz')
            print('\nDate and time : ', formatted_datetime)
            # Display the header row for the data table.
            print('\n  Sample', end='')
            for channel in channels_128:
                print('     Channel Temperature', channel, end='')
            for channel in channels_134:
                print('     Channel Pressure', channel, end='')
            print('')
        
        #Register the temperatures values and print them on screen
        samples_per_channel = 0
        for i in range(N_measures):
            # Display the updated samples per channel count
            samples_per_channel += 1
            if terminal_output == True:    
                print('\r{:8d}'.format(samples_per_channel), end='')
                
            # Read a single value from each selected channel for temperature
            for channel in channels_134:
                value_T = hat_134.t_in_read(channel)
                T_array[i,channel] = value_T
                
                #Print the temperature values depending on its type
                if terminal_output == True:    
                    if value_T == mcc134.OPEN_TC_VALUE:
                        print('     Open     ', end='')
                    elif value_T == mcc134.OVERRANGE_TC_VALUE:
                        print('     OverRange', end='')
                    elif value_T == mcc134.COMMON_MODE_TC_VALUE:
                        print('   Common Mode', end='')
                    else:
                        print('{:12.2f} C'.format(value_T), end='')
                        
            # Read a single value from each selected channel for pressure
            for channel in channels_128:
                value_P_volt = hat_128.a_in_read(channel)
                value_P_bar = Volt_to_bar(value_P_volt)
                P_array[i,channel] = value_P_bar
                
                #Print the pressure values
                if terminal_output == True:    
                    print('{:12.2f} bar'.format(value_P_bar), end='')

            stdout.flush()
                
            # Wait the specified interval between reads.
            sleep(delay_between_reads)
            

    except (HatError, ValueError) as error:
        print('\n', error)


    ##Write the data in csv
    import csv
    from datetime import datetime


    # Header
    header = ["N_measure", "Pressure 1", "Temperature 1", "Pressure 2", "Temperature 2"]

    # Open the CSV file and write the header
    with open(data_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date and time", formatted_datetime, "Number of measures : ", N_measures, "Acquisition frequency : ", acq_frequency, 'Hz'])
        writer.writerow(header)

        # Write the data to the file
        for i in range(N_measures):
            row = [i, P_array[i,0], T_array[i,0], P_array[i,1], T_array[i,1]]
            writer.writerow(row)
            
            
            
            
def T_P_disp(channels_134 = (0, 1), channels_128 = (0, 1), delay_between_reads = 0.1):
    '''
    Description :
    Inputs : channels_134 = sensors channel on MC134, channels_128 = sensors channel on MC128, 
    Outputs :
    
    '''
    
    import datetime #Warning : Time and date set by Rasperry Pi internal clock, out of sync if powered down
    
    # Initialisation of MC128
    ## Input parameters
    input_mode = AnalogInputMode.SE
    input_range = AnalogInputRange.BIP_5V

    ## Get an instance of the selected hat device object.
    address = select_hat_device(HatIDs.MCC_128)
    hat_128 = mcc128(address)

    ## Configuration of hat
    hat_128.a_in_mode_write(input_mode)
    hat_128.a_in_range_write(input_range)

    #Initialisation of MC134
    address_134 = select_hat_device(HatIDs.MCC_134)
    hat_134 = mcc134(address_134)
    tc_type = TcTypes.TYPE_K   # change this to the desired thermocouple type
    
        
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    

    ##Get Temperature data and pressure data
    try:        
        for channel in channels_134:
            hat_134.tc_type_write(channel, tc_type)
            
        # Display the header row for the data table.
        for channel in channels_128:
            print('     Channel Temperature', channel, end='')
        for channel in channels_134:
            print('     Channel Pressure', channel, end='')
        print('')
    
        #Register the temperatures values and print them on screen
        while True:
            # Read a single value from each selected channel for temperature
            for channel in channels_134:
                value_T = hat_134.t_in_read(channel)
                
                #Print the temperature values depending on its type
                if value_T == mcc134.OPEN_TC_VALUE:
                    print('     Open     ', end='')
                elif value_T == mcc134.OVERRANGE_TC_VALUE:
                    print('     OverRange', end='')
                elif value_T == mcc134.COMMON_MODE_TC_VALUE:
                    print('   Common Mode', end='')
                else:
                    print('{:12.2f} C'.format(value_T), end='')
                    
            # Read a single value from each selected channel for pressure
            for channel in channels_128:
                value_P_volt = hat_128.a_in_read(channel)
                value_P_bar = Volt_to_bar(value_P_volt)
                
                #Print the pressure values
                if channel == channels_128[-1]:
                    print('{:12.2f} bar'.format(value_P_bar), end='\r')
                else:
                    print('{:12.2f} bar'.format(value_P_bar), end='')

            
            stdout.flush()
                            
            # Wait the specified interval between reads.
            sleep(delay_between_reads)
            #Find a way to delete line to make place for the new one
            
            

    except (HatError, ValueError) as error:
        print('\n', error)

