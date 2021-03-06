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

		if command == 'setservo':
			print("setservo received. angle {0}".format(args[1]))
			angle = float(args[1])
			Car.set_angle(angle)
			client.send(X(OK))
		elif command == 'readservo':
			client.send(X(Car.read_angle()))
			client.send(X(OK))
		else:
			client.send("unknown command.")
			client.send(OK) # Echo back to client
