from RPLCD import CharLCD, cleared, cursor
import RPi.GPIO as GPIO
import time


lcd = CharLCD(pin_rs=19, pin_e=6, pins_data=[23, 24, 22, 27],
			  numbering_mode=GPIO.BCM,
			  cols=20, rows=4, dotsize=8,
			  charmap='A02',
			  auto_linebreaks=True)
			  
def display_temperature_and_pressure(N, T_hot, temperature1, temperature2, pressure1, pressure2):
	# Clear the LCD screen
	lcd.clear()

	# Format temperature and pressure strings
	temperature1_str = "{:<1}={:>3.1f}".format("T1", temperature1)
	temperature2_str = "{:<1}={:>3.1f}".format("T2", temperature2)
	pressure1_str = "{:<1}={:>5.2f}".format("P1", pressure1)
	pressure2_str = "{:<1}={:>5.2f}".format("P2", pressure2)
	T_hot_str = "{:<1}={:>3.1f}".format("TH", T_hot)
	ready_str = "IN>READY"
	N_str = "{:<1}={:>4.0f}".format("N", N)

	# Display temperature and pressure on the LCD screen
	lcd.cursor_pos = (0, 0)
	lcd.write_string(temperature1_str)

	lcd.cursor_pos = (0, 10)
	lcd.write_string(pressure1_str)

	lcd.cursor_pos = (1, 0)
	lcd.write_string(temperature2_str)

	lcd.cursor_pos = (1, 10)
	lcd.write_string(pressure2_str)

	lcd.cursor_pos = (2, 0)
	lcd.write_string(T_hot_str)

	lcd.cursor_pos = (3, 0)
	lcd.write_string(ready_str)

	lcd.cursor_pos = (3, 10)
	lcd.write_string(N_str)

	  
try:
	# Example usage
	temperature1 = 23.1
	temperature2 = 24.6
	pressure1 = 152.12
	pressure2 = 123.23
	N = 1
	T_hot = 35.3

	display_temperature_and_pressure(N, T_hot, temperature1, temperature2, pressure1, pressure2)

	# Wait for 5 seconds before clearing the LCD screen
	time.sleep(1000)
	lcd.clear()

		

except KeyboardInterrupt:
    print("Exiting...")
    lcd.close(clear=True)
    GPIO.cleanup()
