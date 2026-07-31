from time import sleep_ms


class AHT10:

    ADDRESS = 0x38

    def __init__(self, i2c):
        self.i2c = i2c

        self.i2c.writeto(
            self.ADDRESS,
            b"\xE1\x08\x00"
        )

        sleep_ms(20)

    def medir(self):
        # Comando para iniciar medição
        self.i2c.writeto(
            self.ADDRESS,
            b"\xAC\x33\x00"
        )

        sleep_ms(80)

        # Ler os 6 bytes de resposta
        data = self.i2c.readfrom(
            self.ADDRESS,
            6
        )

        # Umidade
        umidade_raw = (
            (data[1] << 12)
            | (data[2] << 4)
            | (data[3] >> 4)
        )

        umidade = (
            umidade_raw * 100
        ) / 1048576

        # Temperatura
        temperatura_raw = (
            ((data[3] & 0x0F) << 16)
            | (data[4] << 8)
            | data[5]
        )

        temperatura = (
            (temperatura_raw * 200)
            / 1048576
        ) - 50

        return temperatura, umidade