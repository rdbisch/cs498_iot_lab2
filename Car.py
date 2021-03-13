import picar_4wd as fc
import time
import numpy as np
import picamera
import picamera.array
import cv2
import subprocess

class _Car:
	"""Provide an easy to use class to encapsualte
	all of the picar_4wd stuff."""
	def __init__(self):
		self.SERVO_OFFSET = 8
		self.servo_angle = 0
		self.last_reading = 0
		self.velocity = (0,0) # Direction, Speed
		self.worldpos = (0,0) 
		self.map = None
		self.set_angle(0)
		self.inMotion = False
		self.motionStarted = None

	def set_angle(self, angle):
		"""Set the servo angle to angle, controlling
		for the offset."""
		self.servo_angle = angle - self.SERVO_OFFSET
		fc.servo.set_angle(angle - self.SERVO_OFFSET)
		time.sleep(0.04) # Constant from picar_4wd/__init__.py  
	
	def read_angle(self):
		"""Returns the current angle we think the servo
		is set at."""
		return self.servo_angle

	def read_worldpos(self):
		return self.worldpos

	def read_velocity(self):
		"""Returns the current internal state of our velocity."""
		return self.velocity

	def updateWorld(self):
		"""If the car has any kind of velocity,
		this function will update our guess at our world
		position."""
		vx = np.cos(self.velocity[0]) * self.velocity[1]
		vy = np.sin(self.velocity[0]) * self.velocity[1]
		t = time.time()
		if self.motionStarted == None: td = 0
		else: td = t - self.motionStarted

		print("In update world, td = {0} (t = {1} and start = {2}). vx,vy={3}".format(td, t, self.motionStarted, (vx,vy)))
		# we were at worldpos at time=motionStarted
		# uppdate so that we're now at worldpos + t*v
		# where t = time() - motionStarted and v is our velocity.
		x = self.worldpos[1] + (t - td)*vx
		y = self.worldpos[0] + (t - td)*vy 
		self.worldpos = (y, x)
		self.motionStarted = t

	def all_stop(self):
		"""Stop all motors and update internal state
		to reflect."""

		fc.forward(0)
		self.updateWorld()
		self.inMotion = False
		self.velocity = (self.velocity[0], 0)
		self.motionStarted = None

	def drive_forwards(self):
		"""Start the car moving forward.  If the car is 
		already moving forward, stop the car and update
		location information first, then start again."""
		if self.inMotion: self.all_stop()

		fc.forward(10)
		self.inMotion = True
		self.motionStarted = time.time()
		self.velocity = (self.velocity[0], 10)

	def drive_backwards(self):
		"""Start the car moving forward.  If the car is 
		already moving forward, stop the car and update
		location information first, then start again."""
		if self.inMotion: self.all_stop()

		fc.backward(10)
		self.inMotion = True
		self.motionStarted = time.time()
		self.velocity = (self.velocity[0], -10)
	
	def set_heading(self, angle):
		"""Turns the car such that the heading is the desired angle.  Note
		 that this is meant to be absolute world angle, not relative."""
		self.all_stop()
		turn = angle - self.velocity[0]
		return self._turnAngle(turn)

	def read_power(self):
		# From picar_4wd/utils.py
		from picar_4wd.adc import ADC
		power_read_pin = ADC('A4')
		power_val = power_read_pin.read()
		power_val = power_val / 4095.0 * 3.3
		# print(power_val)
		power_val = power_val * 3
		power_val = round(power_val, 2)
		return power_val

	def read_temp(self):
		# From picar_4wd/utils.py
		raw_cpu_temperature = subprocess.getoutput("cat /sys/class/thermal/thermal_zone0/temp")
		cpu_temperature = round(float(raw_cpu_temperature)/1000,2)               # convert unit
		#cpu_temperature = 'Cpu temperature : ' + str(cpu_temperature)
		return cpu_temperature

	def _turnAngle(self, angle):
		"""Turn the car by a relative amount.  A positive angle is left"""
		if (angle > 0): return self._turnLeftAngle(angle)
		else: return self._turnRightAngle(-angle)

	def _turnLeftAngle(self, angle):
		"""Turn the car left by a relative angle."""
		# I told it to turn 15, and I think it turned 25
		# so I need to scale this by (15/25) = 3/5
		#2.78 by experimentation.
		duration = (angle /180.) * (1.32)
		fc.turn_left(10)
		time.sleep(duration)
		fc.turn_left(0)
		self.velocity = (self.velocity[0] + angle, self.velocity[1])
		return

	def _turnRightAngle(self, angle):
		"""Turn the car right by a relative angle."""
		#2.78 by experimentation.
		duration = (angle / 180.) * (1.98)
		fc.turn_right(10)
		time.sleep(duration)
		fc.turn_right(0)
		self.velocity = (self.velocity[0] - angle, self.velocity[1])
		return

	def ping(self):
		"""Turn on the ultrasonic sensor and return the results."""
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

	def take_picture(self, width = 640, height = 480):
		"""Take a picture with the raspberry pi camera
		 and return
		 
		 this code from
		 https://picamera.readthedocs.io/en/release-1.10/quickstart.html
		 https://stackoverflow.com/questions/50630045/how-to-turn-numpy-array-image-to-bytes
		"""
		with picamera.PiCamera() as camera:
			with picamera.array.PiRGBArray(camera) as stream:
				camera.resolution = (width, height)
				camera.capture(stream, 'rgb')
				tmp = cv2.cvtColor(stream.array, cv2.COLOR_RGB2BGR)
				success, encoded_image = cv2.imencode('.jpg', tmp)
				print("*** image success {0}".format(success))
				data_encode = np.array(encoded_image)
				str_encode = data_encode.tostring()
				return str_encode

Car = _Car()
