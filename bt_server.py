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

OK = "000111001101111 binary solo" # The humans are dead

def X(s):
	return str(s).encode('utf-8')

def picWrapper():
	data = Car.take_picture()
	data_s = base64.b64encode(np.array(data).tostring())
	size = len(data_s)
	client.send("sendfile {0}".format(size))
	print("Sending data...{0} bytes total".format(size))

	idx = 0
	block_size = 512
	while (block_size*idx) < size:
		idx_start = block_size*idx
		idx_stop  = min(block_size*(idx + 1), size)
		buf = data_s[idx_start:idx_stop]

		print("Sending block {0} bufsize {1}".format(idx, len(buf)))
		client.send(buf)
		idx = idx + 1

	#client.send(data_s)
	#if xtra_bytes_n > 0:
	#	zero_s = np.zeros(xtra_bytes_n, 'uint8').tostring()
	#	client.send(zero_s)

	#client.send("endfile\nendfile\nendfile\nendfile")
	#print("Done sending...")
	return "endfile"

# The keyword is the command.  The tuple is as follows:
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
	"read_temp": (Car.read_temp, None, True)
}

argparse = {
	'f': lambda x: float(x)
}


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

