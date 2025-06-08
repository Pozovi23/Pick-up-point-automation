import RPi.GPIO as GPIO


class Endstop:
    """
    Класс, отвечающий за концретный концевик на роботе
    """
    def __init__(self, endstop_pin):
        """
        Конструктор класса

        :param endstop_pin: номер пина на плате, к которому подключен концевик
        """
        GPIO.setmode(GPIO.BCM)
        self._endstop_pin = endstop_pin
        GPIO.setup(self._endstop_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def is_endstop_triggered(self):
        """
        Функция, проверящая, нажат ли концевик
        :return: True или False
        """
        return GPIO.input(self._endstop_pin) == GPIO.HIGH
