import RPi.GPIO as GPIO


class LineSensor:
    def __init__(self, pin):
        self._sensor_pin = pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._sensor_pin, GPIO.IN)

    def is_triggered(self):
        return GPIO.input(self._sensor_pin)
