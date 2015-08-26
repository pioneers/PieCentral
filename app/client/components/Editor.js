import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import EditorActionCreators from '../actions/EditorActionCreators';
import EditorStore from '../stores/EditorStore';
import 'brace/mode/python';
import 'brace/theme/monokai';
import {Button, ButtonToolbar, Panel} from 'react-bootstrap';

var Editor = React.createClass({
  getInitialState() {
    return {
      code: EditorStore.getCode()
    };
  },
  updateEditor() {
    this.setState({
      code: EditorStore.getCode()
    });
  },
  componentDidMount() {
    EditorStore.on('change', this.updateEditor);
  },
  componentWillUnmount() {
    EditorStore.removeListener('change', this.updateEditor);
  },
  uploadCode() {
    var currentVal = this.refs.CodeEditor.editor.getValue();
    EditorActionCreators.uploadCode(currentVal);
  },
  render() {
    return (
      <Panel header="Code Editor" bsStyle="primary">
        <ButtonToolbar>
          <Button bsSize="small" bsStyle='default' onClick={this.uploadCode}>Upload</Button>
        </ButtonToolbar>
        <AceEditor
          mode="python"
          theme="monokai"
          width="100%"
          ref="CodeEditor"
          name="CodeEditor"
          value = { this.state.code }
        />
      </Panel>
    );
  }
});

export default Editor;
