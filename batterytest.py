from robot_hat.adc import ADC

adc = ADC("A4")
raw_voltage = adc.read_voltage()
print(f"Raw ADC Voltage on Battery: {raw_voltage}")
