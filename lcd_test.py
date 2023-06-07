'''
from RPLCD import CharLCD
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

lcd = CharLCD(cols=20, rows=4, pin_rs=19, pin_e=6, pins_data=[23, 24, 22, 27])
lcd.write_string(u'Hello world!')
'''


from RPLCD import CharLCD
import RPi.GPIO as GPIO

try:

	lcd = CharLCD(pin_rs=19, pin_e=6, pins_data=[23, 24, 22, 27],
				  numbering_mode=GPIO.BCM,
				  cols=20, rows=4, dotsize=8,
				  charmap='A02',
				  auto_linebreaks=True)
				  
	lcd.write_string('Reda!')
	lcd.cursor_pos = (1, 0)
	lcd.write_string('Henri!')
	lcd.cursor_pos = (2, 0)
	lcd.write_string('Enrique!')

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
