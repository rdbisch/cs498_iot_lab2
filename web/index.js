/*
"use strict";
const { strict } = require('assert');
const { fileURLToPath } = require('url')


# This is not to the Raspberry Pi in my fileURLToPath,
# but rather it is to the server that has the bluetooth
# connection to the Raspberry Pi
var server_port = 5000;
var server_addr = "127.0.0.1";
*/

function client() {
    const { net } = require('electron')
    const request = net.request('127.0.0.1:5000/')
    request.on('response', (response) => {
        console.log(`STATUS: ${response.statusCode}`)
        console.log(`HEADERS: ${JSON.stringify(response.headers)}`)
        response.on('data', (chunk) => {
        console.log(`BODY: ${chunk}`)
        })
        response.on('end', () => {
        console.log('No more data in response.')
        })
    });
    request.end();
}

function greeting() {
    var name = document.getElementById("myName").value;
    document.getElementById("greet").innerHTML = "Hello " + name + " !";
    to_server(name);
    client();
}

function forward() {
    /* https://stackoverflow.com/questions/6396101/pure-javascript-send-post-data-without-a-form */
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/forward", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
    //JSON.stringify({
    //    value: value
    //}));
}

function backward() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/reverse", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
}

function all_stop() {
    /* https://stackoverflow.com/questions/6396101/pure-javascript-send-post-data-without-a-form */
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/allstop", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
    //xhr.send(JSON.stringify({
    //    value: value
    //}));
}

function left() {

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/heading", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({ angle: 90 }));
/*
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/angle", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({ angle: 90 }));
*/
}

function right() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/heading", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({ angle: -90 }));
}

function worldpos() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/worldpos", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            var data = JSON.parse(this.responseText);
            document.getElementById("worldheading").innerHTML = "x-pos: " + data.x + " y-pos: " + data.y;
        }
    }
    xhr.send();
}

function readtemp() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/temp", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            var data = JSON.parse(this.responseText);
            document.getElementById("temp").innerHTML = data["temperature"];
        }
    }
    xhr.send();
}

function readpower() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/power", true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            var data = JSON.parse(this.responseText);
            document.getElementById("power").innerHTML = data["power"];
        }
    }
    xhr.send();
}

function takePicture() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/picture", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            var data = JSON.parse(this.responseText);
            document.getElementById("camera").src = "../static/picamera.jpg?" + new Date().getTime();
        }
    }
    xhr.send();    
}