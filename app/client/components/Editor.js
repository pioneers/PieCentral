import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import EditorActionCreators from '../actions/EditorActionCreators';
import EditorStore from '../stores/EditorStore';
import 'brace/mode/python';
import 'brace/theme/monokai';
import {Button, ButtonGroup, ButtonToolbar, Panel, DropdownButton} from 'react-bootstrap';

var Editor = React.createClass({
  getInitialState() {
    return EditorStore.getFile();
  },
  updateEditor() {
    this.setState(EditorStore.getFile());
  },
  componentDidMount() {
    EditorActionCreators.getCode(this.state.filename);
    EditorStore.on('change', this.updateEditor);
  },
  componentWillUnmount() {
    EditorStore.removeListener('change', this.updateEditor);
  },
  saveCode() {
    var currentVal = this.refs.CodeEditor.editor.getValue();
    EditorActionCreators.sendCode(this.state.filename, currentVal);
  },
  render() {
    return (
      <Panel header="Code Editor" bsStyle="primary">
        <ButtonToolbar>
          <ButtonGroup>
            <DropdownButton bsSize="small" title={this.state.filename}></DropdownButton>
          </ButtonGroup>
          <ButtonGroup>
            <Button bsSize="small" bsStyle='default' onClick={this.saveCode}>Save</Button>
          </ButtonGroup>
        </ButtonToolbar>
        <AceEditor
          mode="python"
          theme="monokai"
          width="100%"
          ref="CodeEditor"
          name="CodeEditor"
          value = { this.state.code }
          editorProps={{$blockScrolling: Infinity}}
        />
      </Panel>
    );
  }
});

export default Editor;
