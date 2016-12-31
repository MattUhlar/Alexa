'use strict';

let opn = require('opn');
let http = require('http').createServer().listen(3000);
let io = require('socket.io').listen(http);
let bodyParser = require('body-parser')
let express = require('express')
let app = express()

app.use(bodyParser.urlencoded({extended: false}))
app.use(bodyParser.json())
app.listen(5000)

let display_page = (socket, data, callback) => {
  socket.emit('try existing tab', data, callback);
}

io.sockets.on('connection',(socket) => {
  
  app.post('/display_page', (request, response) => {

    display_page(socket, request.body, (response_data) => {

      if (response_data.create_new_tab == true) {
        opn(response_data.url);
      }

      response.end(JSON.stringify(response_data));
    });
  })
});

