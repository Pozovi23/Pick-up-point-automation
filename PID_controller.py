class PIDController:
    """
    Класс, отвечающий за PID регуляцию
    """
    def __init__(self, Kp=1.0, Ki=0.0, Kd=0.0):
        """
        Конструктор класса

        Коэффициенты PID регулятора

        :param Kp:
        :param Ki:
        :param Kd:
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self._integral = 0
        self._last_error = 0

    def update(self, error):
        """
        Функция, вычисляющая значение, на которое нужно изменить скорость моторов

        :param error: -2.0, -1.0, 0.0, 1.0, 2.0 в зависимости от направления
        :return: Корректирующее значение
        """
        self._integral += error
        derivative = error - self._last_error
        self._last_error = error
        return self.Kp * error + self.Ki * self._integral + self.Kd * derivative
