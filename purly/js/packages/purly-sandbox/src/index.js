import 'codemirror/lib/codemirror.css'
import 'codemirror/mode/python/python'
import './index.css';

import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';
import Layout from "purly-layout";
import CodeMirror from "react-codemirror";


class Sandbox extends React.Component {

  render() {
    let executorEndpoint="http://127.0.0.1:8001/exec"
    let layoutEndpoint="ws://127.0.0.1:8000/model/sandbox/stream"

    return (
      <div>
        <Editor endpoint={ executorEndpoint }/>
        <div id="layout">
          <Layout endpoint={ layoutEndpoint }/>
        </div>
      </div>
    )
  }
}


class Editor extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
			code: "hello = 'world'",
			readOnly: false,
			mode: 'python',
		};
  }

	updateCode = (newCode) => {
		this.setState({
			code: newCode
		});
    if ( this.updateTrigger !== undefined ) {
      clearTimeout(this.updateTrigger)
    }
    let updateView = () => {
      let toSend = JSON.stringify({ code: newCode });
      $.post(this.props.endpoint, toSend);
    }
    this.updateTrigger = setTimeout(updateView, 1500)
	}

	render = () => {
		let options = {
			lineNumbers: true,
			readOnly: false,
			mode: "python"
		};
    let outputEndpoint="ws://127.0.0.1:8000/model/sandbox-output/stream"
		return (
      <div id="editor">
			<CodeMirror
        ref="editor"
        value={this.state.code}
        onChange={this.updateCode}
        options={options}
      />
      <div id="output">
        <Layout endpoint={ outputEndpoint }/>
      </div>
      </div>
		);
	}
};


ReactDOM.render(<Sandbox/>, document.getElementById('app'));
