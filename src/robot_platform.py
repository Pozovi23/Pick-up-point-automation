import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


from endstop import Endstop
from motor import Motor


class Platform:
    """
    Класс, отвечающий за вертикальную и горизонтальную платформу и взаимодействие с ними
    """

    def __init__(self):
        """
        Конструктор класса

        Создаем объекты для всего оборудования, использующегося в платформах

        Паркуем вертикальную и горизонтальную платформы
        """
        GPIO.setmode(GPIO.BCM)
        self._vertical_endstop = Endstop(7)
        self._push_in_endstop = Endstop(8)
        self._push_out_endstop = Endstop(1)
        self._stepper = Motor(0, 5)
        self._horizontal_motor = Motor(21, 20)
        self.lower_until_endstop()
        self.push_in_platform()

    def move(self, moving_time, direction):
        """
        Функция, отвечающая за подъем/опускание вертикальной платформы

        :param moving_time: время движения
        :param direction: направление up/down
        """
        start_time = time.time()
        while time.time() - start_time <= moving_time:
            if self._vertical_endstop.is_endstop_triggered() and direction == "down":
                break

            if direction == "down":
                self._stepper.motor_control("backward")

            if direction == "up":
                self._stepper.motor_control("forward")

        self._stepper.motor_control("break")

    def lower_until_endstop(self):
        """
        Функция, отвечающая за парковку вертикальной платформы
        """
        while not self._vertical_endstop.is_endstop_triggered():
            self._stepper.motor_control("backward")
        self._stepper.motor_control("break")

    def push_in_platform(self):
        """
        Функция, отвечающая за задвигание горизонтальной платформы
        """
        while not self._push_in_endstop.is_endstop_triggered():
            self._horizontal_motor.motor_control("forward")
        self._horizontal_motor.motor_control("break")

    def push_out_platform(self):
        """
        Функция, отвечающая за выдвижение горизонтальной платформы
        """
        while not self._push_out_endstop.is_endstop_triggered():
            self._horizontal_motor.motor_control("backward")
        self._horizontal_motor.motor_control("break")
