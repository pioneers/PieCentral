import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import EditorActionCreators from '../actions/EditorActionCreators';
import EditorStore from '../stores/EditorStore';
import EditorFileTransfer from './EditorFileTransfer';
import 'brace/mode/python';
import 'brace/theme/monokai';
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Panel,
  DropdownButton
} from 'react-bootstrap';

var Editor = React.createClass({
  getInitialState() {
    return EditorStore.getEditorData();
  },
  updateEditorData() {
    this.setState(EditorStore.getEditorData());
  },
  componentDidMount() {
    EditorStore.on('change', this.updateEditorData);
    EditorStore.on('error', this.alertError);
    EditorActionCreators.getCode(this.state.filename);
  },
  componentWillUnmount() {
    EditorStore.removeListener('change', this.updateEditorData);
    EditorStore.removeListener('error', this.alertError);
  },
  alertError(err) {
    alert(err);
  },
  saveCode() {
    EditorActionCreators.sendCode(this.state.filename, this.state.editorCode);
  },
  editorUpdate(newVal) {
    EditorActionCreators.editorUpdate(newVal);
  },
  render() {
    var filenameLabel = (this.state.latestSaveCode == this.state.editorCode)
      ? this.state.filename
      : this.state.filename + '*';
    return (
      <div>
        <ButtonToolbar>
          <ButtonGroup>
            <DropdownButton bsSize="small" title={ filenameLabel }>
            </DropdownButton>
          </ButtonGroup>
          <ButtonGroup>
            <Button bsSize="small" bsStyle='default' onClick={this.saveCode}>
              Save
            </Button>
          </ButtonGroup>
          <EditorFileTransfer filename={this.state.filename} />
        </ButtonToolbar>
        <AceEditor
          mode="python"
          theme="monokai"
          width="100%"
          ref="CodeEditor"
          name="CodeEditor"
          value = { this.state.editorCode }
          onChange={ this.editorUpdate }
          editorProps={{$blockScrolling: Infinity}}
        />
      </div>
    );
  }
});

export default Editor;
