from machine import Pin, I2C, ADC
import ssd1306
import time
from aht10 import AHT10


i2c = I2C(1, scl=Pin(15), sda=Pin(14))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

i2c_aht = I2C(0,scl=Pin(1),sda=Pin(0))
aht10 = AHT10(i2c_aht)


btn_a = Pin(5, Pin.IN, Pin.PULL_UP)
btn_b = Pin(6, Pin.IN, Pin.PULL_UP)

joy_x = ADC(Pin(27))
joy_y = ADC(Pin(26))

def ler_joystick():
    x = joy_x.read_u16()
    y = joy_y.read_u16()

    norm_x = (x - 32768) / 32768
    norm_y = (y - 32768) / 32768

    offset_x = int(norm_x * 6)
    offset_y = int(-norm_y * 3)

    return offset_x, offset_y


def rosto_default(offset_x, offset_y):
    oled.fill(0)

    oled.fill_rect(34 + offset_x, 22 + offset_y, 14, 28, 1)
    oled.fill_rect(80 + offset_x, 22 + offset_y, 14, 28, 1)


    oled.fill_rect(56, 50, 16, 4, 1)

    oled.show()

def rosto_smile():
    oled.fill(0)

    oled.fill_rect(34, 30, 14, 8, 1)
    oled.fill_rect(80, 30, 14, 8, 1)

    oled.fill_rect(50, 44, 28, 10, 1)

    oled.show()

def rosto_angry():
    oled.fill(0)

    oled.line(34, 26, 48, 40, 1)
    oled.line(80, 40, 94, 26, 1)

    oled.fill_rect(56, 50, 16, 3, 1)

    oled.show()

def rosto_sleep():
    oled.fill(0)

    oled.line(34, 36, 48, 36, 1)
    oled.line(80, 36, 94, 36, 1)

    oled.fill_rect(60, 50, 8, 6, 1)
    oled.text("Zz", 52, 40)

    oled.show()

def rosto_cry():
    oled.fill(0)

    oled.fill_rect(34, 22, 14, 28, 1)
    oled.fill_rect(80, 22, 14, 28, 1)

    oled.fill_rect(40, 50, 4, 8, 1)
    oled.fill_rect(86, 50, 4, 8, 1)

    oled.line(56, 54, 72, 50, 1)

    oled.show()


def tela_temperatura():
    temperatura, umidade = aht10.medir()

    oled.fill(0)

    oled.text("AMBIENTE", 30, 5)

    oled.text(
        "Temp:",
        5,
        25
    )

    oled.text(
        "{:.1f} C".format(temperatura),
        55,
        25
    )

    oled.text(
        "Umid:",
        5,
        42
    )

    oled.text(
        "{:.1f} %".format(umidade),
        55,
        42
    )

    oled.show()

expressoes = ["DEFAULT", "SMILE", "ANGRY", "SLEEP", "CRY"]
indice = 0


while True:
    offset_x, offset_y = ler_joystick()

    if not btn_a.value():
        indice = (indice + 1) % len(expressoes)
        time.sleep(0.2)

    if not btn_b.value():
        indice = (indice - 1) % len(expressoes)
        time.sleep(0.2)

    estado = expressoes[indice]

    if estado == "DEFAULT":
        rosto_default(offset_x, offset_y)

    elif estado == "SMILE":
        rosto_smile()

    elif estado == "ANGRY":
        rosto_angry()

    elif estado == "SLEEP":
        rosto_sleep()

    elif estado == "CRY":
        rosto_cry()

    time.sleep(3)
    
    temperatura, umidade = aht10.medir()

    tela_temperatura()

    time.sleep(3)