import RPi.GPIO as GPIO

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
trigger_pin = 17

# Set up the GPIO pin as an input with an initial high state
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define the function to run when the trigger input is detected
def trigger_callback(channel):
    print("Trigger input detected!")

# Add the event detection for the falling edge of the trigger input
GPIO.add_event_detect(trigger_pin, GPIO.FALLING, callback=trigger_callback)

try:
    print("Waiting for trigger input...")
    while True:
        pass

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()

