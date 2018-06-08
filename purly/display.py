from IPython.display import display, HTML
from .utils import index

def output(uri):
    script = '''
    <script type="text/JavaScript">
      $(document).ready(function(){
        var socket = new WebSocket('%s');
        socket.onmessage = function(event) {
          let msg = JSON.parse(event.data);
          for (let i=0; i < msg.length; i ++) {
            update = msg[i];
            let element = $('[data-purly-model=' + update.model + ']')[0];
            if (update.update == 'attributes') {
              Object.keys(update.attributes).forEach(key => {
                let value = update.attributes[key];
                if (value == null) {
                  element.removeAttribute(key);
                } else {
                  element.setAttribute(key, value);
                }
              });
            } else if (update.update == 'children') {
              element.innerHTML = update.children;
            }
          }
          socket.send('{}');
        };
      });
    </script>
    ''' % uri
    return HTML(index(inject=script))
