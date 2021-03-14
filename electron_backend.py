import bluetooth
import numpy as np
import base64
import cv2
from flask import Flask, request

# Flask boiler-plate
app = Flask(__name__)
host = "DC:A6:32:9C:02:43" # The address of Raspberry PI Bluetooth adapter on the server.

port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))

# Wrapper to abstract bluetooth communications
def car_send(msg):
    """Send message via bluetooth and log to the console."""
    print(">> {0}".format(msg))
    sock.send(msg)
    data = sock.recv(1024)
    print("<< {0}".format(data))
    return { "response": data }

# Wrapper to receive file
def recv_file(msg):
    """This is the counter-procedure to btserver's
     picwrapper.  Once we know we're receiving a file,
     we get sent the total number of bytes and prepare to receive
     the file in a number of bytes."""
    msg = msg["response"].decode('utf-8')
    print("<< {0}".format(msg))
    msg_s = msg.split(" ")
    if (msg_s[0] != "sendfile"): 
        print("Expecting 'sendfile', but received {0}".format(msg_s[0]))

    picdata_s = int(msg_s[1])
    print("Expecting {0} bytes of file".format(picdata_s))

    block_size = 512
    data_b64 = bytearray()
    idx = 0
    while (idx*block_size < picdata_s):
        block = sock.recv(1024)
        print ("received block {0} size {1}".format(idx, len(block)))
        data_b64 = data_b64 + block
        idx = idx + 1

    """This is just a sync to make sure both server and client
    are aligned."""
    print("Waiting endfile")
    end = sock.recv(1024)
    assert(end == b'endfile')
    print("Received endfile")

    """These are just the opposite of the encoding steps done
     on the server.  I am not sure base64 is needed."""
    data = base64.b64decode(data_b64)
    nparr = np.fromstring(data, np.uint8)
    img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite('static/picamera.jpg', img_decode)
    return { "success": True }

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
    res = request.get_json()
    print("in set_angle... request.json is {0}".format(res))
    a = res["angle"]
    return car_send("set_angle {0}".format(a))

@app.route('/worldpos', methods=['GET'])
def worldpos():
    """This is just splitting up a float tuple,
    as a string, into two strings."""
    r = car_send("read_worldpos")
    r = r["response"].decode('utf-8')
    s = r.split(",")
    x = s[0][1:]
    y = s[1][:-1]
    return { "x": x, "y": y }

@app.route('/heading', methods=['GET', 'POST'])
def heading():
    """Depending on the method this stub is called, two
    effects are present.  It makes sense sementically to call
    these both "/heading".

    With POST, and an arugment called "angle", will instruct
    the car to face that heading.  (This is in world coordinates with
    north as 0).

    With GET, the car's current heading is returned."""
    error = None
    if request.method == 'POST':
        res = request.get_json()
        print("/heading POST res={0}".format(res))
        a = float(res["angle"])
        return car_send("set_heading {0}".format(a))
    elif request.method == 'GET':
        result = car_send("read_heading")
        return float(result)

@app.route('/ping', methods=['GET'])
def ping():
    """Call's the car's ultrasonic sensor and return the reading."""
    result = car_send("ping")
    return float(result)

@app.route('/picture', methods=['POST'])
def picture():
    """Take a picture with the camera."""
    result = car_send("take_picture")
    return recv_file(result)

@app.route('/temp', methods=['GET'])
def temp():
    """Read the temperature of the raspberry pi and return the result."""
    result = car_send("read_temp")
    return { "temperature": float(result["response"].decode('utf-8')) }

@app.route('/power', methods=['GET'])
def power():
    result = car_send("read_power")
    return { "power": float(result["response"].decode('utf-8')) }

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    """Flask boilerplate to start the server."""
    #Disable multithreaded so we only maintain
    # one bluetooth connection
    app.run(threaded=False)