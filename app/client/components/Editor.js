import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import EditorActionCreators from '../actions/EditorActionCreators';
import EditorStore from '../stores/EditorStore';
import EditorFileTransfer from './EditorFileTransfer';
import EditorFileCreateDelete from './EditorFileCreateDelete';
import 'brace/mode/python';
import 'brace/theme/monokai';
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Panel,
  DropdownButton,
  MenuItem
} from 'react-bootstrap';
import _ from 'lodash';

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
  loadFilenames() {
    EditorActionCreators.getFilenames();
  },
  changeFile(event, eventKey) {
    EditorActionCreators.setFilename(this.state.filenames[event]);
    EditorActionCreators.getCode(this.state.filenames[event]);
  },
  render() {
    var filenameLabel = (this.state.latestSaveCode == this.state.editorCode)
      ? this.state.filename
      : this.state.filename + '*';
    return (
      <div>
        <ButtonToolbar>
          <ButtonGroup>
            <DropdownButton
              bsSize="small"
              title={ filenameLabel }
              onClick={this.loadFilenames}
              onSelect={this.changeFile}>
              {this.state.filenames.map((filename, index)=> {
                if (filename !== this.state.filename)
                  return <MenuItem key={index} eventKey={String(index)}>{filename}</MenuItem>;
              })}
            </DropdownButton>
          </ButtonGroup>
          <ButtonGroup>
            <Button bsSize="small" bsStyle='default' onClick={this.saveCode}>
              Save
            </Button>
          </ButtonGroup>
          <EditorFileCreateDelete filename={this.state.filename}/>
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
