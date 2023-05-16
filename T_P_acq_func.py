
# Acquiring the T and P data
from __future__ import print_function
from time import sleep
from sys import stdout
from daqhats import mcc134, HatIDs, HatError, TcTypes
from daqhats_utils import select_hat_device, tc_type_to_string

import numpy as np




def T_P_acq_csv(acq_frequency = 1, N_measures = 10, terminal_output = True, data_filename = "data.csv"):
    #Returns a csv data file with Pressure and Temperature data before and after microchip
    #acq_frequency in Herz, max acq_frequency for Temperature is 1 Hz (cf. manufacturer datasheet)
    #Set terminal_output to false if you don't want terminal; output
    
    import datetime #Warning : Time and date set by Rasperry Pi intenarl clock, out of sync if powered down
    
    tc_type = TcTypes.TYPE_K   # change this to the desired thermocouple type
    delay_between_reads = 1/acq_frequency # #To specify, Seconds
    channels = (0, 1) #To specify, of MC134
    T_array = np.zeros((N_measures,len(channels))) # List of temperatures for both sensors in Celsius
    P_array = np.zeros((N_measures,len(channels))) #To complete once pressure sensors is hooked up
        
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    

    ##Get Temperature data and soon pressure data
    try:
        # Get an instance of the selected hat device object.
        address = select_hat_device(HatIDs.MCC_134)
        hat = mcc134(address)
        
        for channel in channels:
            hat.tc_type_write(channel, tc_type)
            
        if terminal_output == True:    
            print('\nAcquiring data ... Press Ctrl-C to abort')
            print('\nNumber of measures : ', N_measures,'Acquisition frequency : ', acq_frequency,'Hz')
            print('\nDate and time : ', formatted_datetime)
            # Display the header row for the data table.
            print('\n  Sample', end='')
            for channel in channels:
                print('     Channel', channel, end='')
            print('')
        
        #Register the temperatures values and print them on screen
        samples_per_channel = 0
        for i in range(N_measures):
            # Display the updated samples per channel count
            samples_per_channel += 1
            if terminal_output == True:    
                print('\r{:8d}'.format(samples_per_channel), end='')
            # Read a single value from each selected channel.
            for channel in channels:
                value = hat.t_in_read(channel)
                T_array[i,channel] = value
                #Print the temperature values depending on its type
                if terminal_output == True:    
                    if value == mcc134.OPEN_TC_VALUE:
                        print('     Open     ', end='')
                    elif value == mcc134.OVERRANGE_TC_VALUE:
                        print('     OverRange', end='')
                    elif value == mcc134.COMMON_MODE_TC_VALUE:
                        print('   Common Mode', end='')
                    else:
                        print('{:12.2f} C'.format(value), end='')

            stdout.flush()
                
            # Wait the specified interval between reads.
            sleep(delay_between_reads)
            
        #print(T_array)


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
