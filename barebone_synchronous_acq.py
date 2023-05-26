from __future__ import print_function
from sys import stdout
from daqhats import hat_list, mcc128, OptionFlags, HatIDs, TriggerModes, \
    HatError, AnalogInputMode, AnalogInputRange
from daqhats_utils import enum_mask_to_string, chan_list_to_mask, \
    validate_channels, input_mode_to_string, input_range_to_string




def select_hat_devices(filter_by_id, number_of_devices):
    """
    This function performs a query of available DAQ HAT devices and determines
    the addresses of the DAQ HAT devices to be used in the example.  If the
    number of HAT devices present matches the requested number of devices,
    a list of all mcc128 objects is returned in order of address, otherwise the
    user is prompted to select addresses from a list of displayed devices.

    Args:
        filter_by_id (int): If this is :py:const:`HatIDs.ANY` return all DAQ
            HATs found.  Otherwise, return only DAQ HATs with ID matching this
            value.
        number_of_devices (int): The number of devices to be selected.

    Returns:
        list[mcc128]: A list of mcc128 objects for the selected devices
        (Note: The object at index 0 will be used as the master).

    Raises:
        HatError: Not enough HAT devices are present.

    """
    selected_hats = []

    # Get descriptors for all of the available HAT devices.
    hats = hat_list(filter_by_id=filter_by_id)
    number_of_hats = len(hats)

    # Verify at least one HAT device is detected.
    if number_of_hats < number_of_devices:
        error_string = ('Error: This example requires {0} MCC 128 HATs - '
                        'found {1}'.format(number_of_devices, number_of_hats))
        raise HatError(0, error_string)
    elif number_of_hats == number_of_devices:
        for i in range(number_of_devices):
            selected_hats.append(mcc128(hats[i].address))
    else:
        # Display available HAT devices for selection.
        for hat in hats:
            print('Address ', hat.address, ': ', hat.product_name, sep='')
        print('')

        for device in range(number_of_devices):
            valid = False
            while not valid:
                input_str = 'Enter address for HAT device {}: '.format(device)
                address = int(input(input_str))

                # Verify the selected address exists.
                if any(hat.address == address for hat in hats):
                    valid = True
                else:
                    print('Invalid address - try again')

                # Verify the address was not previously selected
                if any(hat.address() == address for hat in selected_hats):
                    print('Address already selected - try again')
                    valid = False

                if valid:
                    selected_hats.append(mcc128(address))

    return selected_hats
		
		

	
def read_and_display_data(hat, chan):
    """
    Reads data from the specified channels on the specified DAQ HAT devices
    and updates the data on the terminal display. The reads are executed in a
    loop that continues until either the scan completes or an overrun error
    is detected.

    Args:
        hat (mcc128): A mcc128 HAT device objects.
        chan (list[int]): A list to specify the channel list for the mcc128 HAT device.

    Returns:
        None
    """
    samples_to_read = 500
    timeout = 5  # Seconds
    samples_per_chan_read = [0]
    total_samples_per_chan = [0]
    is_running = True

    # Create blank lines where the data will be displayed
    print('')

    while True:
        data = [None]
        
        # Read the data from the HAT device.
        read_result = hat.a_in_scan_read(samples_to_read, timeout)
        data = read_result.data
        is_running &= read_result.running
        samples_per_chan_read = int(len(data) / len(chan))
        total_samples_per_chan += samples_per_chan_read

        if read_result.buffer_overrun:
            print('\nError: Buffer overrun')
            break
        if read_result.hardware_overrun:
            print('\nError: Hardware overrun')
            break

        # Display the data for the HAT device
        print('HAT')

        # Print the header row for the data table.
        print('  Samples Read    Scan Count', end='')
        print('     Channel', chan, end='')
        print('')

        # Display the sample count information.
        print('{0:>14}{1:>14}'.format(samples_per_chan_read, total_samples_per_chan), end='')

        # Display the data for all selected channels
        for chan_idx in range(len(chan)):
            if samples_per_chan_read[chan_idx] > 0:
                sample_idx = ((samples_per_chan_read[chan_idx] * len(chan)) - len(chan) + chan_idx)	  
                print(' {:>12.5f} V'.format(data[sample_idx]), end='')
        print('\n')

        stdout.flush()

        if not is_running:
            break




    
DEVICE_COUNT = 1

# Define the input modes for the MCC 128
input_mode = AnalogInputMode.SE

# Define the input ranges for the MCC 128
input_range = AnalogInputRange.BIP_5V

# Define the channel list for the HAT device
chan = {0, 1}

# Define the option for the HAT device
option = OptionFlags.EXTCLOCK

samples_per_channel = 10000
sample_rate = 1000.0  # Samples per second

# Get an instance of the selected hat device object.
hats = select_hat_devices(HatIDs.MCC_128, DEVICE_COUNT)

for hat in hats:
    hat.a_in_mode_write(input_mode)
    hat.a_in_range_write(input_range)


# Calculate the actual sample rate.
actual_rate = hat.a_in_scan_actual_rate(len(chan), sample_rate)


                                                         
print('MCC 128 HAT example using external clock option')
print('    Samples per channel:', samples_per_channel)
print('    Requested Sample Rate: {:.3f} Hz'.format(sample_rate))
print('    Actual Sample Rate: {:.3f} Hz'.format(actual_rate))

print('    HAT {}:'.format(0))
print('      Address:', hat.address())
print('      Input mode: ', input_mode_to_string(input_mode))
print('      Input range: ', input_range_to_string(input_range))
print('      Channels: ', chan)
options_str = enum_mask_to_string(OptionFlags, option)
print('      Options:', options_str)

# Start the scan
chan_mask = chan_list_to_mask(chan)
hat.a_in_scan_start(chan_mask, samples_per_channel, sample_rate, option)
					
	
try:
            
	# Read and display data for all devices until scan completes
	# or overrun is detected.
	read_and_display_data(hat, chan)
		


finally:
	hat.a_in_scan_stop()
	hat.a_in_scan_cleanup()




