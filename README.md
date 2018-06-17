[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/rmorshea/purly/master?filepath=examples/notebooks)


# Purly

Control the web with Python.


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


# How It Works

![protocol](https://raw.githubusercontent.com/rmorshea/purly/docs/docs/protocol/protocol.gif)

Purly uses a model server to keep multiple concurrent clients in sync over web sockets. The animation above shows 2 clients - a Python client pushing updates to a single Browser - however you could have more Python clients producing, and more Browser clients consuming, model updates. Each client is associated with a single model (a JSON serializable object), however there can be multiple models that are stored on the server. Clients connect to a particular model by specifying its name in the socket route (e.g. `ws://host:port/<model-name>/stream`). Only clients that are connected to the same model communicate with each other via the model server.


## Protocol

To communicate with the Purly model server you must send JSON serializable arrays which contain objects in the form of a [Message](#message).

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

#### Updates

+ The `content` field specifies changes that will be made to the model.
+ Only differences between the Update `content` and the model are distributed to other clients.


#### Signals

+ A Signal does not modify the state of the model server.
+ Signal `content` is distributed unmodified to other model clients.
