import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import EditorActionCreators from '../actions/EditorActionCreators';
import EditorStore from '../stores/EditorStore';
import 'brace/mode/python';
import 'brace/theme/monokai';
import {Button, ButtonToolbar} from 'react-bootstrap';

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
      <div>
        <AceEditor
          mode="python"
          theme="monokai"
          width="100%"
          ref="CodeEditor"
          name="CodeEditor"
          value = { this.state.code }
        />
        <ButtonToolbar>
          <Button bsStyle='primary' onClick={this.uploadCode}>Upload</Button>
        </ButtonToolbar>
      </div>
    );
  }
});

export default Editor;
