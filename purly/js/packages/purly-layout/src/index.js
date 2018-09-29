import React from 'react';
import ReactDOM from 'react-dom';
import merge from 'deepmerge';
import produce from "immer";
import _ from "lodash";


class Layout extends React.Component {

  models = () => {
    if (this.state) {
      return this.state.models;
    } else {
      return { root: {} };
    }
  }

  send = (msg) => {
    this.toSend.push(msg);
  }

  componentDidMount = () => {
    this.toSend = [];
    this.state = { models: {} };
    this.socket = new WebSocket(this.props.endpoint);
    this.socket.onmessage = this.onMessage;
  }

  componentWillUnmount = () => {
    this.socket.close();
  }

  onMessage = (event) => {

    let reduceModelUpdates = (update, msg) => {
      if (msg.header.type == "update") {
        return merge(update, msg.content);
      } else {
        return update;
      }
    }

    let update = JSON.parse(event.data).reduce(reduceModelUpdates, {});

    if ( !_.isEmpty(update) ) {
      let models = merge(this.models(), update);
      if ( update.root ) {
        let options = { arrayMerge: (target, source) => { return source; } }
        models.root = merge(models.root, update.root, options);
      }
      this.setState({ models });
    }

    let msg = [...this.toSend];
    this.toSend.splice(0, msg.length);
    this.socket.send(JSON.stringify(msg));
  }

  render = () => {
    let models = this.models()
    if (!_.isEmpty(models.root)) {
      let children = Children(this, models.root);
      if ( children.length ){
        return <div>{ children }</div>;
      }
    }
    return <div/>;
  }
}


function Children(layout, model) {
  let children = model.children ? model.children : [];
  return children.map(child => {
    if (typeof child == "object") {
      // the child references another element in models
      let model = layout.models()[child.ref];
      return ( <Element layout={layout} model={model} key={child.ref}/> );
    } else {
      // the child is a raw string
      return child
    }
  })
}


class Element extends React.Component {

  constructor(props) {
    super(props)
    this.state = props.model
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    return nextProps.model;
  }

  shouldComponentUpdate = (nextProps) => {
    let oldSig = this.state.signature;
    let newSig = nextProps.model.signature;
    return ( newSig != oldSig );
  }

  render = () => {
    let model = this.state;
    let Tag = model.tagName;
    let attributes = produce(this.state.attributes, attributes => {
      this.events().map(info => {
        attributes[info.name] = event => {
          this.sendUpdate(info.value.update, model, event.target);
          this.sendEvent(info.value.callback, info.value.keys, event);
        }
      })
    })
    let children = this.children()
    let element
    if ( children.length ) {
      element = ( <Tag {...attributes}>{children}</Tag> );
    } else {
      element = ( <Tag {...attributes}></Tag> );
    }
    return element
  }

  events = () => {
    let array = [];
    for (var name in this.state.attributes) {
      if (this.state.attributes.hasOwnProperty(name)) {
        if (name.startsWith('on') && this.state.attributes[name].callback) {
          array.push({ name: name, value: this.state.attributes[name] });
        }
      }
    }
    return array;
  }

  children = () => {
    let layout = this.props.layout;
    return Children(layout, this.state);
  }

  sendEvent = (callback, keys, event) => {
    let content = {};
    keys.forEach(k => {
      if ( event[k] !== undefined ) {
        content[k] = event[k];
      } else if ( event.nativeEvent[k] !== undefined ) {
        content[k] = event.nativeEvent[k];
      }
    })
    this.props.layout.send({
      header: {
        type: 'signal'
      },
      content: {
        [this.state.attributes.key]: {
          callback: callback,
          event: content
        }
      }
    });
  }

  sendUpdate = (update, model, target) => {
    if (update.length) {
      let content = {}
      update.forEach(k => {
        this.state.attributes[k] = target[k];
        content[k] = target[k];
      })
      this.props.layout.send({
        header: {
          type: 'update'
        },
        content: {
          [this.state.attributes.key]: {
            attributes: content
          }
        }
      });
    }
  }
}


export default Layout
