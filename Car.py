import picar_4wd as fc
import time

class _Car:
	"""Provide an easy to use class to encapsualte
	all the car stuff."""
	def __init__(self):
		self.SERVO_OFFSET = 8
		self.servo_angle = 0
		self.last_reading = 0
		self.velocity = (0,0)
		self.map = None

	def set_angle(self, angle):
		self.servo_angle = angle - self.SERVO_OFFSET
		fc.servo.set_angle(angle - self.SERVO_OFFSET)
		time.sleep(0.04) # Constant from picar_4wd/__init__.py  
	
	def read_angle(self):
		return self.servo_angle

	def ping(self):
		fc.us.trig.low()
		time.sleep(0.1)
		fc.us.trig.high()
		time.sleep(0.00001)
		fc.us.trig.low()
		pulse_end = 0
		pulse_start = 0
		while fc.us.echo.value() == 0: pulse_start = time.time()
		while fc.us.echo.value() == 1: pulse_end = time.time()
		delta = pulse_end - pulse_start
		cm = (343.0/2.0) * (100.0) * delta  # m/s * (cm/m) * time = cm
		self.last_reading = cm
		return cm

Car = _Car()
