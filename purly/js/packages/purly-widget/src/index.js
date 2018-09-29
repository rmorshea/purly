import React from 'react';
import ReactDOM from 'react-dom';
import Layout from 'purly-layout';

window.mountPurlyWidget = function mountPurlyWidget(endpoint, mountId) {
  const mount = document.getElementById(mountId);
  ReactDOM.render(<Layout endpoint={endpoint}/>, mount);
}
