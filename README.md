[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/rmorshea/purly/master?filepath=examples/binders)

# Purly

Control the web with Python.

# Getting Started

Install a dev version (version to pypi coming soon):

```bash
git clone https://github.com/rmorshea/purly && cd purly/ && pip install -e . -r requirements.txt
```

## Using Jupyter

If you're working with the [Jupyter Notebook](http://jupyter.org/) you can simply run the following in separate cells:

```python
import purly

purly.state.Machine().daemon()
```

```python
purly.display.output('ws://127.0.0.1:8000/model/stream')
```

```python
layout = purly.Layout('ws://127.0.0.1:8000/model/stream')

div = layout.html('div')
layout.children.append(div)
div.style.update(height='20px', width='20px', background_color='coral')
```

![getting started notebook gif](https://github.com/rmorshea/purly/blob/master/docs/getting-started-notebook.gif)

## Using The Browser

Run `python run.py` where the file `run.py` contains the following:

```python
import purly

purly.state.Machine().run()
```

Open a your browser and navigate to http://127.0.0.1:8000/ before continuing.

Now you can open up a Python interpreter window and run the following:

```python
layout = purly.Layout('ws://127.0.0.1:8000/model/stream')

div = layout.html('div')
layout.children.append(div)
div.style.update(height='20px', width='20px', background_color='coral')
```

You should now see that a div has magically appeared in the browser page you opened!

![div with some styling](https://raw.githubusercontent.com/rmorshea/purly/master/docs/getting-started-div.png)
