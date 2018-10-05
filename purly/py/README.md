[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/rmorshea/purly/master?filepath=examples)


# Purly

Control the web with Python :snake:


# Install

To install a stable version:

```bash
pip install purly
```

To install a dev version:

> be sure to install [`npm`](https://www.npmjs.com/get-npm) first!

```bash
# clone the repository
git clone https://github.com/rmorshea/purly
cd purly && bash scripts/build.sh && bash scripts/install.sh
```

# Getting Started

Run the following snippet of code, and then navigate to http://127.0.0.1:8000/model/index.

```python
import purly

# Prepare your layout
purly.state.Machine().run(debug=False)
layout = purly.Layout('ws://127.0.0.1:8000/model/stream')

# create your HTML
div = layout.html('div')
div.style.update(height='20px', width='20px', background_color='coral')

# add it to the layout
layout.children.append(div)

# and sync it!
layout.sync()
```

Now your creation should have magically appeared in the browser page you opened!

![div with some styling](https://raw.githubusercontent.com/rmorshea/purly/master/docs/getting-started-div.png)


# Architecture (Not Final)

Purly's fundamental goal is to give Python as much control of a webpage as possible, and do so in one incredibly simple package. There is one major problem that stands in the way of this goal - data synchronization. Purly's answer to this problem is its [model server](#model-server) which acts as a "source of truth" about the [state of a webpage](#model-specification) for any clients which connect to it and adhere to its [protocol](#communication-protocol).


## Model Server

![protocol](https://raw.githubusercontent.com/rmorshea/purly/master/docs/protocol/protocol.gif)

Purly uses a web socket server to keep multiple concurrent clients in sync. The animation above shows 2 clients - a Python client pushing updates to a single Browser - however you could have more clients producing and / or consuming, model updates. Each client is associated with a single model (any JSON serializable object), however there can be multiple models that are stored on the server. Clients connect to a particular model by specifying its name in the socket route (e.g. `ws://host:port/model/<model-name>/stream`). Only clients that are connected to the same model communicate with each other via the server.


## Model Specification

While the Model Server supports any JSON serializable model, Purly, as a framework for controlling the web must:

1. Communicate as fully as possible the structure of DOM elements and their various interactions.
2. Send updates to DOM models over a network in short and easy to interpret packages:
  + Update messages must be small in size in order to reduce network traffic.

To accomplish the goals defined above we propose a flat DOM model:

```python
Model = {
  id: Element,
  # Maps a uniquely identifiable string to an Element.
  root: Element,
  # The id "root" should always indicate the outermost Element.
  ...
}
```

```python
Element = {
  tagName: string
  # Standard HTML tags like h1, table, div, etc.
  signature: string
  # The hash of this element attributes, and the hashes of its children.
  children: [
    string,
    # Any arbitrary string.
    {type: 'ref', 'ref': string},
    # An object where the key "ref" refers to the "key" attribute.
    ...
  ],
  attributes: {
    key: id,
    # The id that uniquely identifies this Element.
    parent_key: id
    # The unique id of this element's parent.
    attr: value,
    # Map any attribute name to any JSON serializable value.
    on<Event>: {
      # Specify an event callback with an attribute of the form "on<Event>".
      callback: uuid,
      # A unique identifier by which to refer to the callback function.
      keys: [...],
      # Details of the event to pass on to the callback.
      update: [...]
      # Any attributes that should be synced before the callback is triggered.
    }
  }
}
```


### Purly Model Example

The following HTML

```html
<div key='root'>
  Make a selection:
  <input type='text' key='abc123'></input>
<div>
```

would be communicated with the following Purly model:

```python
{
  root: {
    tag: 'div',
    elements: [
      'Make a selection:'
      {'ref': 'abc123'},
    ]
    attributes: {
      'key': 'root'
    }
  },
  abc123: {
    tag: 'input',
    elements: [],
    attributes: {
      'key': 'abc123',
      'type': 'text',
    },
  }
}
```


## Communication Protocol

The Purly model server sends and receives JSON serializable arrays which contain objects in the form of a [Message](#message).

```python
[
  Message,
  # a dict conforming to the Message spec
  ...
]
```


### Message

There are two types of messages - Updates and Signals - however both conform to the following format.

```python
Message = {
  "header": {
    "type": "signal" or "update",
    # Message type (indicates the kind of content).
    "version": "0.1",
    # Message protocol version.
  }
  # Content which depends on the message type.
  "content": dict,
}
```


#### Signals

+ A Signal does not modify the state of the model server.
+ Signal `content` is distributed unmodified to other model clients.


#### Updates

+ The `content` field specifies changes that will be merged into the model.
+ Only the differences between the Update `content` and the model are distributed to other clients.
+ Update merges are performed in a nested fashion

If the current state of the model is

```python
{
  'a': {
    'b': 1,
    'c': 1,
  }
}
```

and an update message

```python
{
  'a': {
    'c': 2
  }
}
```

is received, the resulting model state is

```python
{
  'a': {
    'b': 1,
    'c': 2,
  }
}
```
