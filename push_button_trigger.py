import RPi.GPIO as GPIO
from T_P_acq_func import T_P_acq_csv, T_P_disp

"""
Purpose:
    

Description:


"""

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
trigger_pin = 14


# Set up the GPIO pin as an input with an initial high state
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)




def trigger_callback(channel):
    """
    Purpose:

    Args:

    """
    pin_state = GPIO.input(trigger_pin)
    print('Button Pushed', pin_state)



# Add the event detection for the falling edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.RISING, callback=trigger_callback)


try:
    print("Waiting for trigger input...")
    while True:
        pass

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
