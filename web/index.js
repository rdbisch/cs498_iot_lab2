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