import RPi.GPIO as GPIO


class Motor:
    """
    Класс, отвечающий за конкретный мотор робота
    """
    def __init__(self, in1, in2):
        """
        Конструктор класса

        Принимает два значения выводных пинов для управления моторами
        :param in1
        :param in2

        Запускает ШИМ-модуляцию
        """
        self._in1 = in1
        self._in2 = in2
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._in1, GPIO.OUT)
        GPIO.setup(self._in2, GPIO.OUT)

        self._pwm_frequency = 1000
        self._pwm_in1 = GPIO.PWM(self._in1, self._pwm_frequency)
        self._pwm_in2 = GPIO.PWM(self._in2, self._pwm_frequency)

        self._pwm_in1.start(0)
        self._pwm_in2.start(0)

    def motor_control(self, state, speed=100):
        """
        Функция, изменяющая скорость мотора путем изменения скважности ШИМ-сигнала

        :param state: forward - вперед, backward - назад, stop - остановка, break - удержание
        :param speed: скорость
        """
        speed = max(0, min(100, speed))

        if state == "forward":
            self._pwm_in1.ChangeDutyCycle(speed)
            self._pwm_in2.ChangeDutyCycle(0)
        elif state == "backward":
            self._pwm_in1.ChangeDutyCycle(0)
            self._pwm_in2.ChangeDutyCycle(speed)
        elif state == "stop":
            self._pwm_in1.ChangeDutyCycle(0)
            self._pwm_in2.ChangeDutyCycle(0)
        elif state == "break":
            self._pwm_in1.ChangeDutyCycle(100)
            self._pwm_in2.ChangeDutyCycle(100)

    def __del__(self):
        self._pwm_in1.stop()
        self._pwm_in2.stop()
        GPIO.cleanup()
