import React from 'react';
import global from './global'
import _ from 'lodash'

function Layout(props) {
  let children = PurlyChildren(global.models.root.children);
  let component = ( <div>{ children }</div> );
  return component;
}

function PurlyChildren(children) {
  children = children ? children : [];
  return children.map(c => {
    if (typeof c === "object") {
      return PurlyElement(global.models[c.ref]);
    } else {
      return c;
    }
  })
}

function PurlyElement(model) {

  let component;
  let Tag = model.tag;
  let key = model.attributes.key;
  let children = PurlyChildren(model.children);
  let attributes = model.attributes;
  let propertyNames = [];

  for (var property in attributes) {
    if (attributes.hasOwnProperty(property)) {
      if (property.startsWith('on') && attributes[property].callback) {
        let prop = attributes[property];
        attributes[property] = (function(event) {
          sendUpdate(key, prop.update, event.target);
          sendEvent(key, prop.callback, prop.keys, event);
        });
      }
      propertyNames.push(property);
    }
  }
  if (children.length) {
    component = ( <Tag {...attributes}>{children}</Tag> );
  } else {
    component = ( <Tag {...attributes}/> );
  }
  return component;
}

function sendEvent(key, callback, keys, event) {
  let content = {};
  keys.forEach(k => {
    content[k] = event[k];
  })
  global.toSend.push({
    header: {
      type: 'signal'
    },
    content: {
      [key]: {
        callback: callback,
        event: content
      }
    }
  });
}

function sendUpdate(key, update, state) {
  if (update.length) {
    let content = {}
    update.forEach(k => {
      content[k] = state[k];
    })
    global.toSend.push({
      header: {
        type: 'update'
      },
      content: {
        [key]: {
          attributes: content
        }
      }
    });
  }
}

export default Layout
