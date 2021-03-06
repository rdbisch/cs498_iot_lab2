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

commands = {
	"set_angle": (Car.set_angle, 'f'),
	"read_angle": (Car.read_angle, None),
	"set_heading": (Car.set_heading, 'f'),
	"read_heading": (Car.read_velocity, None),
	"drive_forwards": (Car.drive_forwards, None),
	"drive_backwards": (Car.drive_backwards, None),
	"ping": (Car.ping, None),
	"take_picture": (Car.take_picture, None)		
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
			func, arg = commands[command]
			if arg in argparse: 
				parsed_arg = argparse[arg](args[1])
				client.send("Received command {0} with arg {1}".format(func, parsed_arg))
				result = func(parsed_arg)
				client.send(result)
			elif arg == None:
				client.send("Received comamnd {0}".format(func))
				result = func()
				client.send(result)
			else:
				raise "Invalid argument {0} for function {1}".format(arg, func)

		else:
			client.send("unknown command.")

