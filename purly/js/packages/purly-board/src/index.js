import React from 'react';
import ReactDOM from 'react-dom';
import Layout from "purly-layout";

const uri = document.location.hostname + ":" + document.location.port;
var url = (uri + document.location.pathname).split("/").slice(0, -1);
url[url.length - 1] = "stream";
var secure = (document.location.protocol == "https:");
if (secure) {
  var protocol = "wss:";
} else {
  var protocol = "ws:";
}
let endpoint = protocol + '//' + url.join('/');
const mount = document.getElementById("react-mount");
ReactDOM.render(<Layout endpoint={endpoint}/>, mount);
