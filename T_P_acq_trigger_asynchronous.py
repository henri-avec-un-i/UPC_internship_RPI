"""

With current synchronization signal from sync box, this script doesn't work. Need a single trigger signal at the beginning of the acquisition in order to work properly,
not a trigger signal at each frame

"""


import RPi.GPIO as GPIO
from T_P_acq_func import T_P_acq_csv, T_P_disp
from RPLCD import CharLCD, cleared, cursor

"""
Purpose:
    Display continuously real time T and P data and save it to a csv file when a trigger input is detected

    Description:
        This script displays real time T and P data with the function
        T_P_disp() (see doc in source file T_P_acq_func). When a trigger
        input is detected, a csv file containing a recording of T and P
        values is saved. You can change acquisition parameters by modifying 
        T_P_acq_csv() arguments

"""
################################################

"""
Hardware initialisation
"""

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
trigger_pin = 17


# Set up the GPIO pin as an input with an initial high state
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

### Definition of script constants
T_hot_wall = 50 # Hot wall temperature in Celcius, to specify, in Celcius, to measure later directly on the Peltier module
pressure_alarm = 130 #Pressure alarm threshold in bar for alarm and system shutdown

################################################


def data_array_update(channel):
    """
    Callback function to be executed when the trigger input is detected.

    Args:
        channel (int): The GPIO channel number that triggered the callback.
    """
    print("Acquiring temperature and pressure data in csv...")
    T_P_acq_csv(channels_134=(0, 1), channels_128=(0, 1), acq_frequency=10, N_measures=50, terminal_output=True, data_filename="data.csv", alarm_on = True, pressure_alarm = 130)
    print("Data saved in csv!")

# Add the event detection for the rising edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.RISING, callback=data_array_update)


try:
    print("Waiting for trigger input...")
    while True:
        T_P_disp(lcd, T_hot_wall, channels_134=(0, 1), channels_128=(0, 1), delay_between_reads=1, alarm_on = True, pressure_alarm = 130)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
