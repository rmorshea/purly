# Purly

Control the web with Python.

# Getting Started

```python
import purly

purly.state.Machine().daemon()
```

Open a new browser tab or page and navigate to http://127.0.0.1:8000/ before continuing.

```python
layout = purly.Layout('ws://127.0.0.1:8000/model/stream')

div = layout.html('div')
layout.children.append(div)
div.style.update(height='20px', width='20px', background_color='coral')
```

You should now see that a div has magically appeared!

![div with some styling](https://github.com/rmorshea/purly/docs/getting-started-div.png)
