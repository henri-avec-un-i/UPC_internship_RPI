from RPLCD import CharLCD, cleared, cursor
import RPi.GPIO as GPIO
from time import sleep


lcd = CharLCD(pin_rs=19, pin_e=6, pins_data=[23, 24, 22, 27],
			  numbering_mode=GPIO.BCM,
			  cols=20, rows=4, dotsize=8,
			  charmap='A02',
			  auto_linebreaks=True)
	  
'''
while True:
	lcd.write_string('Reda!')
	lcd.cursor_pos = (1, 0)
	lcd.write_string('Henri!')
	lcd.cursor_pos = (2, 0)
	lcd.write_string('Enrique!')
	sleep(0.1)
	lcd.clear()
	sleep(0.1)
'''

'''
try:
	while True:	  
		lcd.write_string('Reda!')
		lcd.cursor_pos = (1, 0)
		lcd.write_string('Henri!')
		lcd.cursor_pos = (2, 0)
		lcd.write_string('Enrique!')
		#sleep(0.1)
		#lcd.clear()
		#sleep(0.1)
'''

smiley = (
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b10001,
    0b10001,
    0b01110,
    0b00000,
)

lcd.create_char(0, smiley)
lcd.write_string(unichr(0))

try:
	while True:	
		pass


except KeyboardInterrupt:
    print("Exiting...")
    lcd.clear()
    GPIO.cleanup()
