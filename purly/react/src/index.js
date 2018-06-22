import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import Layout from './Layout';
import deepmerge from 'deepmerge'
import global from './global'

const uri = document.location.hostname + ":" + document.location.port;
var url = (uri + document.location.pathname).split("/");
url[url.length - 1] = "stream"
const socket = new WebSocket("ws://" + url.join('/'));
const mount = document.getElementById('react-mount');

socket.onmessage = function onMessage(event) {
  let diffs = 0;
  JSON.parse(event.data).forEach(msg => {
    if ( msg.header.type === "update" ) {
      global.models = deepmerge(global.models, msg.content);
      diffs ++;
    }
  })
  if ( diffs && global.models.root ) {
    // Only render if the root node has been defined.
    ReactDOM.render(<Layout/>, mount);
  }
  // send messages
  let msg = [...global.toSend];
  global.toSend.splice(0, msg.length);
  socket.send(JSON.stringify(msg));
}
