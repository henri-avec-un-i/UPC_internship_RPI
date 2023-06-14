import RPi.GPIO as GPIO
from T_P_acq_func import T_P_acq_csv, T_P_disp

"""
Purpose:
    Display continuously real time T and P data and save it to a csv file when a trigger input is detected

    Description:
        This script displays real time T and P data with the function
        T_P_disp() (see doc in source file T_P_acq_func). When a trigger
        input is detected, a csv file containing a recording of T and P
        values. You can change acquisition parameters by modifying 
        T_P_acq_csv() arguments

"""

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
trigger_pin = 17


# Set up the GPIO pin as an input with an initial high state
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)




def trigger_callback(channel):
    """
    Callback function to be executed when the trigger input is detected.

    Args:
        channel (int): The GPIO channel number that triggered the callback.
    """
    print("Acquiring temperature and pressure data in csv...")
    T_P_acq_csv(channels_134=(0, 1), channels_128=(0, 1), acq_frequency=10, N_measures=50, terminal_output=False, data_filename="data.csv", alarm_on = True, pressure_alarm = 130)
    print("Data saved in csv!")

# Add the event detection for the falling edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.FALLING, callback=trigger_callback)


try:
    print("Waiting for trigger input...")
    while True:
        T_P_disp(channels_134=(0, 1), channels_128=(0, 1), delay_between_reads=1, alarm_on = True, pressure_alarm = 130)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
