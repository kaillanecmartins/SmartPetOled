from machine import Pin, I2C, ADC
import ssd1306
import time
from aht10 import AHT10
import network
import ntptime

WIFI_SSID = "kaillane"
WIFI_PASSWORD = "20240712"

CIDADE = "Sao Luis"
PAIS = "MA"

# UTC-3
FUSO_HORARIO = -3

TEMPO_TELA = 5000  # 5 segundos

i2c = I2C(
    1,
    scl=Pin(15),
    sda=Pin(14)
)

oled = ssd1306.SSD1306_I2C(
    128,
    64,
    i2c
)

i2c_aht = I2C(
    0,
    scl=Pin(1),
    sda=Pin(0)
)

aht10 = AHT10(i2c_aht)


btn_a = Pin(
    5,
    Pin.IN,
    Pin.PULL_UP
)

btn_b = Pin(
    6,
    Pin.IN,
    Pin.PULL_UP
)



joy_x = ADC(Pin(27))
joy_y = ADC(Pin(26))


def conectar_wifi():

    wlan = network.WLAN(
        network.STA_IF
    )

    wlan.active(True)

    if not wlan.isconnected():

        print("Conectando ao Wi-Fi...")

        wlan.connect(
            WIFI_SSID,
            WIFI_PASSWORD
        )

        tentativas = 0

        while not wlan.isconnected():

            time.sleep(0.5)

            tentativas += 1

            if tentativas >= 20:

                print("Falha ao conectar ao Wi-Fi")

                return None

    print("Wi-Fi conectado")
    print("IP:", wlan.ifconfig()[0])

    return wlan



def sincronizar_hora():

    print("Sincronizando horario...")

    try:

        ntptime.settime()

        print(
            "Horario UTC:",
            time.localtime()
        )

        return True

    except Exception as erro:

        print(
            "Erro ao sincronizar:",
            erro
        )

        return False



def hora_brasil():

    agora = time.localtime()

    ano = agora[0]
    mes = agora[1]
    dia = agora[2]

    hora = agora[3]
    minuto = agora[4]
    segundo = agora[5]

    hora += FUSO_HORARIO

    if hora < 0:

        hora += 24
        dia -= 1

    elif hora >= 24:

        hora -= 24
        dia += 1

    return hora, minuto, segundo



def ler_joystick():

    x = joy_x.read_u16()
    y = joy_y.read_u16()

    norm_x = (
        x - 32768
    ) / 32768

    norm_y = (
        y - 32768
    ) / 32768

    offset_x = int(
        norm_x * 6
    )

    offset_y = int(
        -norm_y * 3
    )

    return offset_x, offset_y


def rosto_default(
    offset_x,
    offset_y
):

    oled.fill(0)

    oled.fill_rect(
        34 + offset_x,
        22 + offset_y,
        14,
        28,
        1
    )

    oled.fill_rect(
        80 + offset_x,
        22 + offset_y,
        14,
        28,
        1
    )

    oled.fill_rect(
        56,
        50,
        16,
        4,
        1
    )

    oled.show()


def rosto_smile():

    oled.fill(0)

    oled.fill_rect(
        34,
        30,
        14,
        8,
        1
    )

    oled.fill_rect(
        80,
        30,
        14,
        8,
        1
    )

    oled.fill_rect(
        50,
        44,
        28,
        10,
        1
    )

    oled.show()


def rosto_angry():

    oled.fill(0)

    oled.line(
        34,
        26,
        48,
        40,
        1
    )

    oled.line(
        80,
        40,
        94,
        26,
        1
    )

    oled.fill_rect(
        56,
        50,
        16,
        3,
        1
    )

    oled.show()


def rosto_sleep():

    oled.fill(0)

    oled.line(
        34,
        36,
        48,
        36,
        1
    )

    oled.line(
        80,
        36,
        94,
        36,
        1
    )

    oled.fill_rect(
        60,
        50,
        8,
        6,
        1
    )

    oled.text(
        "Zz",
        52,
        40
    )

    oled.show()


def rosto_cry():

    oled.fill(0)

    oled.fill_rect(
        34,
        22,
        14,
        28,
        1
    )

    oled.fill_rect(
        80,
        22,
        14,
        28,
        1
    )

    oled.fill_rect(
        40,
        50,
        4,
        8,
        1
    )

    oled.fill_rect(
        86,
        50,
        4,
        8,
        1
    )

    oled.line(
        56,
        54,
        72,
        50,
        1
    )

    oled.show()


def tela_temperatura():

    try:

        temperatura, umidade = aht10.medir()

        oled.fill(0)

        oled.text(
            "AMBIENTE",
            30,
            5
        )

        oled.text(
            "Temp:",
            5,
            25
        )

        oled.text(
            "{:.1f} C".format(
                temperatura
            ),
            55,
            25
        )

        oled.text(
            "Umid:",
            5,
            42
        )

        oled.text(
            "{:.1f} %".format(
                umidade
            ),
            55,
            42
        )

        oled.show()

    except Exception as erro:

        print(
            "Erro no AHT10:",
            erro
        )

        oled.fill(0)

        oled.text(
            "ERRO SENSOR",
            20,
            25
        )

        oled.show()



def tela_horario():

    hora, minuto, segundo = hora_brasil()

    oled.fill(0)

    oled.text(
        "HORARIO",
        35,
        5
    )

    oled.text(
        "{:02d}:{:02d}".format(
            hora,
            minuto
        ),
        44,
        25
    )

    oled.text(
        CIDADE,
        32,
        43
    )

    oled.text(
        PAIS,
        57,
        54
    )

    oled.show()


expressoes = [
    "DEFAULT",
    "SMILE",
    "ANGRY",
    "SLEEP",
    "CRY"
]

indice = 0


wifi = conectar_wifi()

if wifi is not None:

    sincronizar_hora()

else:

    print(
        "Continuando sem Wi-Fi"
    )



telas = [
    "ROSTO",
    "AMBIENTE",
    "HORARIO"
]

tela_atual = 0

ultima_troca = time.ticks_ms()


while True:

    offset_x, offset_y = ler_joystick()


    if not btn_a.value():

        indice = (
            indice + 1
        ) % len(expressoes)

        print(
            "Expressao:",
            expressoes[indice]
        )

        time.sleep_ms(200)


    if not btn_b.value():

        indice = (
            indice - 1
        ) % len(expressoes)

        print(
            "Expressao:",
            expressoes[indice]
        )

        time.sleep_ms(200)

    agora = time.ticks_ms()

    if time.ticks_diff(
        agora,
        ultima_troca
    ) >= TEMPO_TELA:

        tela_atual = (
            tela_atual + 1
        ) % len(telas)

        ultima_troca = agora


    if telas[tela_atual] == "ROSTO":

        estado = expressoes[indice]

        if estado == "DEFAULT":

            rosto_default(
                offset_x,
                offset_y
            )

        elif estado == "SMILE":

            rosto_smile()

        elif estado == "ANGRY":

            rosto_angry()

        elif estado == "SLEEP":

            rosto_sleep()

        elif estado == "CRY":

            rosto_cry()


    elif telas[tela_atual] == "AMBIENTE":

        tela_temperatura()


    elif telas[tela_atual] == "HORARIO":

        tela_horario()


    time.sleep_ms(50)