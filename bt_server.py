import bluetooth
import numpy as np
import base64
from Car import Car

hostMACAddress = "DC:A6:32:9C:02:43" # The address of Raspberry PI Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
port = 0
backlog = 1
size = 1024
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.bind((hostMACAddress, port))
s.listen(backlog)

# Wrapper to encode. In the event
# I need to change it, this allows me to 
# change it only once.
def X(s):
	return str(s).encode('utf-8')

# This is a speical routine 
#  to facilitate transferring files over BlueTooth
# The basic idea is to send ahead of time the number of bytes
#  to expect, and then send them over in small chunks.
def picWrapper():
	data = Car.take_picture()
	data_s = base64.b64encode(np.array(data).tostring())
	size = len(data_s)
	client.send("sendfile {0}".format(size))
	print("Sending data...{0} bytes total".format(size))

	# idx will keep track of which block we're on.
	idx = 0
	block_size = 512
	while (block_size*idx) < size:
		idx_start = block_size*idx
		idx_stop  = min(block_size*(idx + 1), size)
		buf = data_s[idx_start:idx_stop]

		print("Sending block {0} bufsize {1}".format(idx, len(buf)))
		client.send(buf)
		idx = idx + 1

	return "endfile"

# This command dictionary contains the "protocol" for how
#  we communicate back and forth to the other server.  
# Given that the dictionary is a set of Key->value pairs.  
#  In this case, the Key is the "string" command that will be
#  sent to us via bluetooh.  The Value is a 3-tuple with elements:
#  [0] - Function call
#  [1] - How to parse the argument, if any
#  [2] - True if output needs to be encoded
commands = {
	"set_angle": (Car.set_angle, 'f', True),
	"read_angle": (Car.read_angle, None, True),
	"set_heading": (Car.set_heading, 'f', True),
	"read_heading": (Car.read_velocity, None, True),
	"drive_forwards": (Car.drive_forwards, None, True),
	"drive_backwards": (Car.drive_backwards, None, True), 
	"ping": (Car.ping, None, True),
	"take_picture": (picWrapper, None, False),
	"all_stop": (Car.all_stop, None, True),
	"read_power": (Car.read_power, None, True),
	"read_temp": (Car.read_temp, None, True),
	"read_worldpos": (Car.read_worldpos, None, True)
}

# This is a dictionary of functions to call for different 
#  argument parsing options.  We only have 'f' now but who 
#  knows what we'll need later.
argparse = {
	'f': lambda x: float(x)
}

# This is the main loop.  It simply listens
#  for strings coming through on BlueTooth
#  and parsing them according to the rules we
#  defined in the Command dictionary.
print("listening on port ", port)
client, clientInfo = s.accept()
while 1:
	print("server recv from: ", clientInfo)
	data = client.recv(size)
	print(data)
	if data:
		data = str(data.decode('utf-8'))
		args = data.split(' ')
		print("Received data {0} args {1}".format(data, args))
		command = args[0]

		if command in commands:
			func, arg, encode = commands[command]
			result = None
			if arg in argparse: 
				parsed_arg = argparse[arg](args[1])
				print("<< Received command {0} with arg {1}".format(command, parsed_arg))
				result = func(parsed_arg)
			elif arg == None:
				print("<< Received comamnd {0}".format(command))
				result = func()
			else:
				raise "Invalid argument {0} for function {1}".format(arg, func)

			if encode: client.send(X(result))
			else: client.send(result)

		else:
			client.send("unknown command.")
