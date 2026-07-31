from machine import Pin, I2C
from aht10 import AHT10

i2c_aht = I2C(
    0,
    sda=Pin(0),
    scl=Pin(1)
)

print("Dispositivos:", i2c_aht.scan())

sensor = AHT10(i2c_aht)

temperatura, umidade = sensor.medir()

print("Temperatura:", temperatura)
print("Umidade:", umidade)