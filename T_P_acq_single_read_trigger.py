import RPi.GPIO as GPIO
from T_P_acq_func import *

"""
Purpose:

Description:


"""

## GPIO pins set up
# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
trigger_pin = 17

# Set up the GPIO pin as an input with an initial high state
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)



# Initialisation of data_array
column_labels = ['Time', 'T1', 'T2', 'P1', 'P2'] # To modify as desired
data_array = []







rising_edge_counter = 0


def trigger_callback(channel):
    """
    Callback function to be executed when the trigger input is detected.

    Args:
        channel (int): The GPIO channel number that triggered the callback.
    """
    
    if rising_edge_counter == 0:
        start_time = time.time()
        #Single read T and P, append the values to the data array, write time also

    
    else:
        current_time = time.time()
        relative_time = current_time - start_time
        #Single read T and P, append the values to the data array, write time also
        

    
    #Increment the rising edge counter, ie index of P and T measure
    rising_edge_counter += 1


# Add the event detection for the falling edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.FALLING, callback=trigger_callback)


try:
    
    while True:
        T_P_disp(channels_134=(0, 1), channels_128=(0, 1), delay_between_reads=1, alarm_on = True, pressure_alarm = 130)



except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
