[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/rmorshea/purly/master?filepath=examples/notebooks)


# Purly

A networked framework for controlling the web.


# Install

Install a dev version (version to pypi coming soon):

```bash
git clone https://github.com/rmorshea/purly && cd purly/ && pip install -e . -r requirements.txt
```


# Getting Started

Run `python run.py` where the file `run.py` contains the following:

```python
import purly

purly.state.Machine().run()
```

Open a your browser and navigate to http://127.0.0.1:8000/model before continuing.

Now you can open up a Python interpreter window and run the following:

```python
layout = purly.Layout('ws://127.0.0.1:8000/model/stream')

div = layout.html('div')
div.style.update(height='20px', width='20px', background_color='coral')
layout.children.append(div)
layout.sync()
```

You should now see that a div has magically appeared in the browser page you opened!

![div with some styling](https://raw.githubusercontent.com/rmorshea/purly/master/docs/getting-started-div.png)


# Architecture (Not Final)

Purly's fundamental goal is to give Python as much control of a webpage as possible, and do so in one incredibly simple package. There is one major problem that stands in the way of this goal - data synchronization. Purly's answer to this problem is its [model server](#model-server) which acts as a "source of truth" about the [state of a webpage](#model-specification) for any clients which connect to it and adhere to its [protocol](#communication-protocol).


## Model Server

![protocol](https://raw.githubusercontent.com/rmorshea/purly/master/docs/protocol/protocol.gif)

Purly uses a web socket server to keep multiple concurrent clients in sync. The animation above shows 2 clients - a Python client pushing updates to a single Browser - however you could have more clients producing and / or consuming, model updates. Each client is associated with a single model (any JSON serializable object), however there can be multiple models that are stored on the server. Clients connect to a particular model by specifying its name in the socket route (e.g. `ws://host:port/<model-name>/stream`). Only clients that are connected to the same model communicate with each other via the server.


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
  'root': Element,
  # The id "root" should always indicate the outermost Element.
  ...
}
```

```python
Element = {
  tag: str
  # Standard HTML tags like h1, table, div, etc.
  children: [
    str,
    # Any arbitrary string.
    {'ref': str},
    # An object where the key "ref" refers to the "data-purly-model" attribute.
    ...
  ]
  attributes: {
    'data-purly-model': id,
    # The id that uniquely identifies this Element.
    'attr': value,
    # Map any attribute name to any JSON serializable value.
    ...
  }
  events: [
    str,
    # A string indicating an event this Element reacts to.
    ...
  ]
}
```


### Purly Model Example

The following HTML

```html
<div data-purly-model='root'>
  <h1 data-purly-model='abc123'>Hello World!</p>
<div>
```

Would be communicate with the following Purly model:

```python
{
  'root': {
    tag: 'div',
    elements: [
      {'ref': 'abc123'},
    ]
    attributes: {
      'data-purly-model': 'root'
    }
    events: []
  },
  'abc123': {
    tag: 'h1',
    elements: [
      'Hello World!'
    ],
    attributes: {
      'data-purly-model',
    },
    events: []
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
{
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
