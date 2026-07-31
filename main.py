from machine import Pin, I2C, ADC
import ssd1306
import time
import random
from aht10 import AHT10
import network
import ntptime


#configurações de wifi
WIFI_SSID = ""
WIFI_PASSWORD = ""

CIDADE = "Sao Luis"
PAIS = "MA"

# São Luís = UTC-3
FUSO_HORARIO = -3

# Tempo de cada tela
TEMPO_TELA = 5000




INTERVALO_PISCADA_MIN = 4000
INTERVALO_PISCADA_MAX = 9000

INTERVALO_OLHAR_MIN = 5000
INTERVALO_OLHAR_MAX = 12000



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



expressoes = [
    "DEFAULT",
    "SMILE",
    "ANGRY",
    "SLEEP",
    "CRY"
]

indice = 0



telas = [
    "ROSTO",
    "AMBIENTE",
    "HORARIO"
]

tela_atual = 0



estado_animacao = "NORMAL"

olhar_auto_x = 0
olhar_auto_y = 0

inicio_animacao = time.ticks_ms()

proxima_piscada = time.ticks_add(
    time.ticks_ms(),
    random.randint(
        INTERVALO_PISCADA_MIN,
        INTERVALO_PISCADA_MAX
    )
)

proximo_olhar = time.ticks_add(
    time.ticks_ms(),
    random.randint(
        INTERVALO_OLHAR_MIN,
        INTERVALO_OLHAR_MAX
    )
)


ultima_troca_tela = time.ticks_ms()


ultima_temperatura = 0
ultima_umidade = 0

ultima_leitura_sensor = 0

INTERVALO_SENSOR = 2000


def conectar_wifi():

    wlan = network.WLAN(
        network.STA_IF
    )

    wlan.active(True)

    if not wlan.isconnected():

        print("Conectando ao Wi-Fi...")

        try:

            wlan.connect(
                WIFI_SSID,
                WIFI_PASSWORD
            )

        except Exception as erro:

            print(
                "Erro ao iniciar Wi-Fi:",
                erro
            )

            return None

        tentativas = 0

        while not wlan.isconnected():

            time.sleep_ms(500)

            tentativas += 1

            if tentativas >= 20:

                print(
                    "Falha ao conectar ao Wi-Fi"
                )

                return None

    print("Wi-Fi conectado")

    print(
        "IP:",
        wlan.ifconfig()[0]
    )

    return wlan



def sincronizar_hora():

    print(
        "Sincronizando horario..."
    )

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

    hora = agora[3]
    minuto = agora[4]
    segundo = agora[5]

    hora += FUSO_HORARIO

    if hora < 0:

        hora += 24

    elif hora >= 24:

        hora -= 24

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

    # Zona morta
    if abs(norm_x) < 0.15:

        norm_x = 0

    if abs(norm_y) < 0.15:

        norm_y = 0

    # Movimento horizontal
    offset_x = int(
        norm_x * 7
    )

    # Movimento vertical invertido
    offset_y = int(
        -norm_y * 4
    )

    return offset_x, offset_y




def desenhar_circulo_preenchido(
    cx,
    cy,
    raio,
    cor=1
):

    for y in range(
        -raio,
        raio + 1
    ):

        valor = (
            raio * raio
            - y * y
        )

        largura = int(
            valor ** 0.5
        )

        oled.fill_rect(
            cx - largura,
            cy + y,
            largura * 2 + 1,
            1,
            cor
        )



def desenhar_olho(
    x,
    y,
    largura=18,
    altura=32
):

    oled.fill_rect(
        x,
        y,
        largura,
        altura,
        1
    )


def olhos_normais(
    offset_x=0,
    offset_y=0
):

    desenhar_olho(
        30 + offset_x,
        16 + offset_y,
        18,
        32
    )

    desenhar_olho(
        80 + offset_x,
        16 + offset_y,
        18,
        32
    )



def rosto_default(
    offset_x,
    offset_y
):

    oled.fill(0)

    olhos_normais(
        offset_x,
        offset_y
    )

    # Boca pequena
    oled.fill_rect(
        56,
        52,
        16,
        4,
        1
    )

    oled.show()


def rosto_smile():

    oled.fill(0)

    # Olho esquerdo sorrindo

    oled.line(
        30,
        34,
        39,
        28,
        1
    )

    oled.line(
        39,
        28,
        48,
        34,
        1
    )

    # Olho direito sorrindo

    oled.line(
        80,
        34,
        89,
        28,
        1
    )

    oled.line(
        89,
        28,
        98,
        34,
        1
    )

    # Sorriso

    desenhar_circulo_preenchido(
        64,
        49,
        13,
        1
    )

    # Remove parte superior
    # deixando somente a curva

    oled.fill_rect(
        48,
        38,
        32,
        12,
        0
    )

    oled.show()


def rosto_angry():

    oled.fill(0)

    # Sobrancelha/olho esquerdo

    oled.line(
        30,
        24,
        48,
        32,
        1
    )

    oled.line(
        30,
        25,
        48,
        35,
        1
    )

    # Sobrancelha/olho direito

    oled.line(
        80,
        32,
        98,
        24,
        1
    )

    oled.line(
        80,
        35,
        98,
        25,
        1
    )

    # Boca

    oled.fill_rect(
        55,
        51,
        18,
        4,
        1
    )

    oled.show()



def rosto_sleep():

    oled.fill(0)

    # Olho esquerdo fechado

    oled.fill_rect(
        30,
        32,
        18,
        4,
        1
    )

    # Olho direito fechado

    oled.fill_rect(
        80,
        32,
        18,
        4,
        1
    )

    # Boca

    oled.fill_rect(
        60,
        51,
        8,
        5,
        1
    )

    # Z

    oled.text(
        "Z",
        51,
        20
    )

    oled.text(
        "z",
        94,
        15
    )

    oled.show()



def rosto_cry():

    oled.fill(0)

    # Olho esquerdo

    desenhar_olho(
        30,
        16,
        18,
        32
    )

    # Olho direito

    desenhar_olho(
        80,
        16,
        18,
        32
    )

    # Lágrima esquerda

    desenhar_circulo_preenchido(
        39,
        51,
        3,
        1
    )

    oled.fill_rect(
        36,
        50,
        6,
        8,
        1
    )

    # Lágrima direita

    desenhar_circulo_preenchido(
        89,
        51,
        3,
        1
    )

    oled.fill_rect(
        86,
        50,
        6,
        8,
        1
    )

    # Boca triste

    oled.line(
        56,
        55,
        64,
        51,
        1
    )

    oled.line(
        64,
        51,
        72,
        55,
        1
    )

    oled.show()



def rosto_blink():

    oled.fill(0)

    # Olho esquerdo fechado

    oled.fill_rect(
        30,
        31,
        18,
        5,
        1
    )

    # Olho direito fechado

    oled.fill_rect(
        80,
        31,
        18,
        5,
        1
    )

    # Boca

    oled.fill_rect(
        56,
        52,
        16,
        4,
        1
    )

    oled.show()



def atualizar_sensor():

    global ultima_temperatura
    global ultima_umidade
    global ultima_leitura_sensor

    agora = time.ticks_ms()

    if time.ticks_diff(
        agora,
        ultima_leitura_sensor
    ) < INTERVALO_SENSOR:

        return

    ultima_leitura_sensor = agora

    try:

        (
            ultima_temperatura,
            ultima_umidade
        ) = aht10.medir()

        print(
            "Temperatura:",
            ultima_temperatura,
            "C | Umidade:",
            ultima_umidade,
            "%"
        )

    except Exception as erro:

        print(
            "Erro no AHT10:",
            erro
        )



def tela_temperatura():

    atualizar_sensor()

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
            ultima_temperatura
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
            ultima_umidade
        ),
        55,
        42
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


wifi = conectar_wifi()

if wifi is not None:

    sincronizar_hora()

else:

    print(
        "Continuando sem Wi-Fi"
    )


def iniciar_piscada():

    global estado_animacao
    global inicio_animacao

    estado_animacao = "PISCANDO"

    inicio_animacao = time.ticks_ms()


def atualizar_animacao():

    global estado_animacao
    global inicio_animacao
    global proxima_piscada
    global proximo_olhar
    global olhar_auto_x
    global olhar_auto_y

    agora = time.ticks_ms()


    if estado_animacao == "NORMAL":

        if time.ticks_diff(
            agora,
            proxima_piscada
        ) >= 0:

            iniciar_piscada()

            return


    elif estado_animacao == "PISCANDO":

        if time.ticks_diff(
            agora,
            inicio_animacao
        ) >= 120:

            estado_animacao = "NORMAL"

            proxima_piscada = time.ticks_add(
                agora,
                random.randint(
                    INTERVALO_PISCADA_MIN,
                    INTERVALO_PISCADA_MAX
                )
            )

            proximo_olhar = time.ticks_add(
                agora,
                random.randint(
                    INTERVALO_OLHAR_MIN,
                    INTERVALO_OLHAR_MAX
                )
            )

    if estado_animacao == "NORMAL":

        if time.ticks_diff(
            agora,
            proximo_olhar
        ) >= 0:

            olhar_auto_x = random.choice(
                [-5, 0, 5]
            )

            olhar_auto_y = random.choice(
                [-2, 0, 2]
            )

            estado_animacao = "OLHANDO"

            inicio_animacao = agora

    elif estado_animacao == "OLHANDO":

        if time.ticks_diff(
            agora,
            inicio_animacao
        ) >= 1000:

            olhar_auto_x = 0
            olhar_auto_y = 0

            estado_animacao = "NORMAL"

            proximo_olhar = time.ticks_add(
                agora,
                random.randint(
                    INTERVALO_OLHAR_MIN,
                    INTERVALO_OLHAR_MAX
                )
            )


def atualizar_rosto(
    offset_x,
    offset_y
):

    estado = expressoes[indice]

    if estado_animacao == "PISCANDO":

        rosto_blink()

        return

    if estado == "DEFAULT":

        final_x = (
            offset_x +
            olhar_auto_x
        )

        final_y = (
            offset_y +
            olhar_auto_y
        )

        # Limite horizontal

        if final_x > 7:

            final_x = 7

        if final_x < -7:

            final_x = -7

        # Limite vertical

        if final_y > 4:

            final_y = 4

        if final_y < -4:

            final_y = -4

        rosto_default(
            final_x,
            final_y
        )


    elif estado == "SMILE":

        rosto_smile()


    elif estado == "ANGRY":

        rosto_angry()

    elif estado == "SLEEP":

        rosto_sleep()

    elif estado == "CRY":

        rosto_cry()



oled.fill(0)

oled.text(
    "Hello!",
    45,
    25
)

oled.show()

time.sleep_ms(1500)



#reset temporizadores
proxima_piscada = time.ticks_add(
    time.ticks_ms(),
    random.randint(
        INTERVALO_PISCADA_MIN,
        INTERVALO_PISCADA_MAX
    )
)

proximo_olhar = time.ticks_add(
    time.ticks_ms(),
    random.randint(
        INTERVALO_OLHAR_MIN,
        INTERVALO_OLHAR_MAX
    )
)

ultima_troca_tela = time.ticks_ms()


while True:

    agora = time.ticks_ms()

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


    if time.ticks_diff(
        agora,
        ultima_troca_tela
    ) >= TEMPO_TELA:

        tela_atual = (
            tela_atual + 1
        ) % len(telas)

        ultima_troca_tela = agora


    atualizar_animacao()


    if telas[tela_atual] == "ROSTO":

        atualizar_rosto(
            offset_x,
            offset_y
        )

    elif telas[tela_atual] == "AMBIENTE":

        tela_temperatura()

    elif telas[tela_atual] == "HORARIO":

        tela_horario()

    time.sleep_ms(50)