import RPi.GPIO as GPIO
from T_P_acq_func import *

#Script to display continuously temperature and pressure data while waiting for an external trigger input. Records 
#data in csv file when receiving an external trigger input

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
trigger_pin = 17

# Set up the GPIO pin as an input with an initial high state
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define the function to run when the trigger input is detected
def trigger_callback(channel):
    print("Acquiring temperature and pressure data in csv...")
    T_P_acq_csv(channels_134 = (0, 1), channels_128 = (0, 1), acq_frequency = 10, N_measures = 50, terminal_output = False, data_filename = "data.csv")
    print("Data saved in csv !")
    

# Add the event detection for the falling edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.FALLING, callback=trigger_callback)

try:
    print("Waiting for trigger input...")
    while True:
        T_P_disp(channels_134 = (0, 1), channels_128 = (0, 1), delay_between_reads = 1)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
