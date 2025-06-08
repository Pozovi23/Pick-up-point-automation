import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None  # или используйте заглушку


from line_sensor import LineSensor
from motor import Motor
from PID_controller import PIDController


class LineFollower:
    """
    Класс, отвечающий за движение и повороты робота
    """

    def __init__(self):
        """
        Конструктор класса

        Создаем объекты для всего оборудования, использующегося при движении
        """
        GPIO.setmode(GPIO.BCM)
        self._left_line_sensor = LineSensor(pin=17)
        self._right_line_sensor = LineSensor(pin=4)
        self._center_line_sensor = LineSensor(pin=14)

        self._left_motor = Motor(in1=24, in2=23)
        self._right_motor = Motor(in1=27, in2=22)

        self.left_turn_sensor = LineSensor(pin=2)
        self.right_turn_sensor = LineSensor(pin=3)

        self._forward_pid = PIDController(Kp=50, Ki=0.0005, Kd=0.3)
        self._base_speed = 40
        self._last_error = 0
        self._turn_time = 0.4
        self._go_forward_time = 0.2
        self._search_speed = 90

    def _constrain_speed(self, speed):
        """
        Функция, отвечающая за ограничение скорости в диапазоне [-100; 100] для исключения ошибок
        :param speed: текущая скорость
        :return: скорость в диапазоне [-100; 100]
        """
        return max(-100, min(100, speed))

    def _calculate_error(self):
        """
        Функция, отвечающая за вычисление ошибки движения робота, чтобы в дальнейшем скомпенсировать её

        2.0 - сильное отклонение вправо
        1.0 - умеренное отклонение вправо
        0.0 - робот едет идеально по линии
        -1.0 - умеренное отклонение влево
        -2.0 - сильное отклонение влево
        :return: коэффициент ошибки
        """
        left_state = self._left_line_sensor.is_triggered()
        right_state = self._right_line_sensor.is_triggered()
        center_state = self._center_line_sensor.is_triggered()

        if left_state and not center_state and not right_state:
            return 2.0  # Strong left deviation
        elif not left_state and not center_state and right_state:
            return -2.0  # Strong right deviation
        elif left_state and center_state and not right_state:
            return 1.0  # Mild left deviation
        elif not left_state and center_state and right_state:
            return -1.0  # Mild right deviation
        elif not left_state and center_state and not right_state:
            return 0.0  # Centered
        else:
            return self._last_error

    def _move_with_pid(self):
        """
        Функция, регулирующая движение робота

        В процессе работы вызывает calculate_error() и
            на основе полученного значения вычисляет коррекционное значение с помощью PID-регулятора
            и уже с помощью него изменяет скорость моторов.
        """
        error = self._calculate_error()
        self._last_error = error

        correction = self._forward_pid.update(error)

        # Calculate motor speeds
        left_speed = self._base_speed - correction
        right_speed = self._base_speed + correction
        left_speed = self._constrain_speed(left_speed)
        right_speed = self._constrain_speed(right_speed)

        self._left_motor.motor_control(
            "forward" if left_speed >= 0 else "backward", abs(left_speed)
        )
        self._right_motor.motor_control(
            "forward" if right_speed >= 0 else "backward", abs(right_speed)
        )

    def _turn_right(self):
        """
        Функция, поворачивающая робота вправо, чтобы он начал искать линию после поворота
            и продолжил движение по заданной графом траектории
        """
        self._left_motor.motor_control("forward", self._search_speed)
        self._right_motor.motor_control("backward", self._search_speed)
        time.sleep(self._turn_time)
        self._left_motor.motor_control("backward", 100)
        self._right_motor.motor_control("forward", 100)
        time.sleep(0.02)
        self._left_motor.motor_control("break", 100)
        self._right_motor.motor_control("break", 100)
        time.sleep(0.1)

    def _turn_left(self):
        """
        Функция, поворачивающая робота влево, чтобы он начал искать линию после поворота
            и продолжил движение по заданной графом траектории
        """
        self._left_motor.motor_control("backward", self._search_speed)
        self._right_motor.motor_control("forward", self._search_speed)
        time.sleep(self._turn_time)
        self._left_motor.motor_control("forward", 100)
        self._right_motor.motor_control("backward", 100)
        time.sleep(0.02)
        self._left_motor.motor_control("break", 100)
        self._right_motor.motor_control("break", 100)
        time.sleep(0.1)

    def _go_forward(self):
        """
        Функция, прокатывающая робота вперед, чтобы он начал искать линию
            и продолжил движение по заданной графом траектории
        """
        self._left_motor.motor_control("forward", self._search_speed)
        self._right_motor.motor_control("forward", self._search_speed)
        time.sleep(self._go_forward_time)

    def _find_line_after_turn(self, which_turn):
        """
        Функция, которая инициирует поиск линии после поворота, согласованно с which turn
        :param which_turn: left, right. Позволяет понять где искать линию после поворота
        :return: найдена линия в течение пяти секунд или нет
        """
        found = False

        start_time = time.time()

        while not found and time.time() - start_time < 5:
            if which_turn == "right":
                self._left_motor.motor_control("forward", self._search_speed)
                self._right_motor.motor_control("backward", self._search_speed)
            elif which_turn == "left":
                self._left_motor.motor_control("backward", self._search_speed)
                self._right_motor.motor_control("forward", self._search_speed)

            if self._center_line_sensor.is_triggered():
                if which_turn == "right":
                    self._left_motor.motor_control("backward", 100)
                    self._right_motor.motor_control("forward", 100)
                    time.sleep(0.02)
                    self._left_motor.motor_control("break", 100)
                    self._right_motor.motor_control("break", 100)
                    time.sleep(0.1)

                else:
                    self._left_motor.motor_control("forward", 100)
                    self._right_motor.motor_control("backward", 100)
                    time.sleep(0.02)
                    self._left_motor.motor_control("break", 100)
                    self._right_motor.motor_control("break", 100)
                    time.sleep(0.1)

                self._left_motor.motor_control("break", 100)
                self._right_motor.motor_control("break", 100)
                time.sleep(1)
                found = True

        return found

    def handle_intersection(self, which_turn):
        """
        Функция, инициирующая поворот или движение прямо (в зависимости от which_turn)
            и нахождение линии
        :param which_turn: left, forward, right. В зависимости от значения робот поедет в нужную сторону
        """
        self._left_motor.motor_control("stop", 0)
        self._right_motor.motor_control("stop", 0)
        time.sleep(2)
        self._left_motor.motor_control("break", 0)
        self._right_motor.motor_control("break", 0)
        time.sleep(1)
        self._left_motor.motor_control("stop", 0)
        self._right_motor.motor_control("stop", 0)
        time.sleep(1)

        if which_turn == "right":
            self._turn_right()
            self._left_motor.motor_control("stop", 0)
            self._right_motor.motor_control("stop", 0)
            time.sleep(1)
            if not self._find_line_after_turn(which_turn):
                print("Line not found")
                exit(0)
            self._last_error = 2
        elif which_turn == "left":
            self._turn_left()
            self._left_motor.motor_control("stop", 0)
            self._right_motor.motor_control("stop", 0)
            time.sleep(1)
            self._last_error = -2
            if not self._find_line_after_turn(which_turn):
                print("Line not found")
                exit(0)
        elif which_turn == "forward":
            self._go_forward()
            self._left_motor.motor_control("break", 100)
            self._right_motor.motor_control("break", 100)
            time.sleep(1)
            self._last_error = 0

    def move_straight(self):
        """
        Функция, инициирующая движение
        """
        self._move_with_pid()

    def hard_stop(self):
        """
        Резкая остановка робота
        """
        self._left_motor.motor_control("break", 100)
        self._right_motor.motor_control("break", 1000)
        time.sleep(1)
