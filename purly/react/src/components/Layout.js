import React from 'react';

function Layout(models) {

  function PurlyChildren(children) {
    children = children ? children : [];
    return children.map(c => {
      if (typeof c === "object") {
        return PurlyElement(models[c.ref]);
      } else {
        return c;
      }
    })
  }

  function PurlyElement(model) {
    let Type = model.tag;
    let children = PurlyChildren(model.children);
    console.log(model);
    return ( <Type {...model.attributes}>{ children }</Type> );
  }

  let children = PurlyChildren(models.root.children);
  let component = ( <div>{ children }</div> );
  return component;
}

export default Layout
