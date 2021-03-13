import bluetooth
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
	"take_picture": (picWrapper None, False),
	"all_stop": (Car.all_stop, None, True),
	"read_power": (Car.read_power, None, True),
	"read_temp": (Car.read_temp, None, True)
}

argparse = {
	'f': lambda x: float(x)
}

def picWrapper():
	data = Car.take_picture()
	data_s = data.encode('utf-8')
	size = len(data) // 1024
	client.send("sendfile {0}".format(size))
	for i in range(size):
		start = 1024*i
		stop = 1024*(i+1)
		stop = min(len(data), stop)
		client.send(data_s[start:stop])
	return "endfile"

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

