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
          global.toSend.push(formUpdate(key, prop.update, event.target));
          global.toSend.push(formEvent(key, prop.callback, prop.keys, event));
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

function formEvent(key, callback, keys, event) {
  let content = {};
  keys.forEach(k => {
    content[k] = event[k];
  })
  return {
    header: {
      type: 'signal'
    },
    content: {
      [key]: {
        callback: callback,
        event: content
      }
    }
  };
}

function formUpdate(key, update, state) {
  if (update.length) {
    let content = {}
    update.forEach(k => {
      content[k] = state[k];
    })
    return {
      header: {
        type: 'update'
      },
      content: {
        [key]: {
          attributes: content
        }
      }
    }
  }
}

export default Layout
