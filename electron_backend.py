import bluetooth
from flask import Flask, request

app = Flask(__name__)
host = "DC:A6:32:9C:02:43" # The address of Raspberry PI Bluetooth adapter on the server.

port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))
#while 1:
#    text = input("Enter your message: ") # Note change to the old (Python 2) raw_input
#    if text == "quit":
#        break
#    sock.send(text)
#
#    data = sock.recv(1024)
#    print("from server: ", data)
#sock.close()

# Wrapper to abstract bluetooth communications
def car_send(msg):
    print(">> {0}".format(msg))
    sock.send(msg)
    data = sock.recv(1024)
    print("<< {0}".format(data))
    return { "response": data }

@app.route('/forward', methods=['POST'])
def forward():
    return car_send("drive_forwards")

@app.route('/allstop', methods=['POST'])
def stopcar():
    return car_send("all_stop")

@app.route('/reverse', methods=['POST'])
def reverse():
    return car_send("drive_backwards")

@app.route('/angle', methods=['GET'])
def angle():
    result = car_send("read_angle")
    return result

@app.route('/set_angle', methods=['POST'])
def set_angle():
    print("in set_angle... request.json is {0}".format(request.get_json()))
    a = float(request.form['angle'])
    return car_send("set_angle {0}".format(a))

@app.route('/heading', methods=['GET', 'POST'])
def heading():
    error = None
    if request.method == 'POST':
        a = float(request.form['heading'])
        car_send("set_heading {0}".format(a))
    elif request.method == 'GET':
        result = car_send("read_heading")
        return float(result)

@app.route('/ping', methods=['GET'])
def ping():
    result = car_send("ping")
    return float(result)

@app.route('/picture', methods=['POST'])
def picture():
    result = car_send("take_picture")
    return result

@app.route('/temp', methods=['GET'])
def temp():
    result = car_send("read_temp")
    return result

@app.route('/power', methods=['GET'])
def power():
    result = car_send("read_power")
    return result

@app.route('/')
def hello_world():
    return 'Hello, World!'
