from IPython.display import display, HTML
from .utils import index

def output(uri):
    script = '''
    <script type="text/JavaScript">
      $(document).ready(function() {
        let models;
        let socket = new WebSocket('%s');

        socket.onmessage = function onFirstMessage(event) {
          models = JSON.parse(event.data);
          if (models.root) {
            handleUpdate({root: models.root});
          }
          socket.onmessage = onMessage;
        }

        function onMessage(event) {
          JSON.parse(event.data).forEach(update => {
            mergeDeep(models, update);
            handleUpdate(update);
          });
          socket.send('{}');
        }

        function handleUpdate(update) {
          let element;
          Object.keys(update).forEach(key => {
            let selection = $('[data-purly-model=' + key + ']');
            Array.from(selection).forEach(element => {
              if (update[key].children) {
                registerChildren(element, update[key].children);
              }
              if (update[key].attributes) {
                let attributes = update[key].attributes;
                Object.keys(attributes).forEach(key => {
                  element.setAttribute(key, attributes[key]);
                })
              }
            });
          })
        }

        function registerChildren(parent, children) {
          let length = parent.children.length;
          for (let i = children.length; i < length; i++) {
            parent.removeChild(parent.lastChild);
          }
          children.forEach((spec, index) => {
            let created;
            if (spec.type == 'ref') {
              if (models[spec.ref]) {
                created = elementFromModel(models[spec.ref]);
              }
            } else {
              // the child is a string
              created = document.createTextNode(spec.str);
            }
            let current = parent.childNodes[index];
            if (current) {
              morphdom(current, created)
            } else {
              parent.appendChild(created);
            }
          })
        }

        function elementFromModel(model) {
          let element = document.createElement(model.tag);
          Object.keys(model.attributes).forEach(key => {
            element.setAttribute(key, model.attributes[key]);
          })
          registerChildren(element, model.children);
          return element;
        }
      });

      function isObject(item) {
        return (item && typeof item === 'object' && !Array.isArray(item));
      }

      function mergeDeep(target, source) {
        if (isObject(target) && isObject(source)) {
          for (const key in source) {
            if (isObject(source[key])) {
              if (!target[key]) Object.assign(target, { [key]: {} });
              mergeDeep(target[key], source[key]);
            } else if (source[key] != null){
              Object.assign(target, { [key]: source[key] });
            } else {
              delete target[key]
            }
          }
        }
        return target
      }
    </script>
    ''' % uri
    return HTML(index(inject=script))
