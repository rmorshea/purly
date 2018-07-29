import React from 'react';
import global from './global'
import _ from 'lodash'

function Layout(props) {
  let children = Children(global.models.root.children);
  let component = ( <div>{ children }</div> );
  return component;
}

function Children(children) {
  children = children ? children : [];
  return children.map(c => {
    if (typeof c === "object") {
      return <Element { ...global.models[c.ref] }/>;
    } else {
      return c;
    }
  })
}

class Element extends React.Component {

  shouldComponentUpdate(nextProps) {
    return this.props.signature != nextProps.signature;
  }

  render() {
    let model = this.props;
    let component;
    let Tag = model.tagName;
    let key = model.attributes.key;
    let children = Children(model.children);
    let attributes = model.attributes;
    let propertyNames = [];

    for (var property in attributes) {
      if (attributes.hasOwnProperty(property)) {
        if (property.startsWith('on') && attributes[property].callback) {
          let prop = attributes[property];
          attributes[property] = (function(event) {
            sendUpdate(key, prop.update, model, event.target);
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

function sendUpdate(key, update, model, target) {
  if (update.length) {
    let content = {}
    update.forEach(k => {
      global.models[key].attributes[k] = target[k];
      content[k] = target[k];
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
