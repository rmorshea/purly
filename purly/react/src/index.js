import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import Layout from './components/Layout';
import deepmerge from 'deepmerge'

var models = {};
const socket = new WebSocket("ws://127.0.0.1:8000/model/example-model/stream");
const mount = document.getElementById('react-mount');

socket.onmessage = function onMessage(event) {
  let diffs = 0;
  JSON.parse(event.data).forEach(msg => {
    if ( msg.header.type === "update" ) {
      models = deepmerge(models, msg.content);
      diffs ++;
    }
  })
  if ( diffs && models.root ) {
    ReactDOM.render(<Layout {...models} />, mount);
  }
  socket.send("[]");
}
