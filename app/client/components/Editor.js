import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import EditorActionCreators from '../actions/EditorActionCreators';
import EditorStore from '../stores/EditorStore';
import EditorToolbar from './EditorToolbar';
import Mousetrap from 'mousetrap';
import 'brace/mode/python';
import 'brace/theme/monokai';

var Editor = React.createClass({
  getInitialState() {
    return EditorStore.getEditorData();
  },
  updateEditorData() {
    this.setState(EditorStore.getEditorData());
  },
  componentDidMount() {
    Mousetrap.prototype.stopCallback = function(e, element, combo) {
      return false; // Always respond to keyboard combos
    };
    Mousetrap.bind(['mod+s'], (e)=>{
      if (e.preventDefault) {
        e.preventDefault();
      }
      this.saveCode();
    });
    EditorStore.on('change', this.updateEditorData);
    EditorStore.on('error', this.alertError);
    EditorActionCreators.getCode(this.state.filename);
  },
  componentWillUnmount() {
    Mousetrap.unbind(['mod+s']);
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
  changeFile(filename) {
    EditorActionCreators.setFilename(filename);
    EditorActionCreators.getCode(filename);
  },
  render() {
    var unsavedChanges = (this.state.latestSaveCode !== this.state.editorCode);
    return (
      <div>
        <EditorToolbar
          unsavedChanges={unsavedChanges}
          filename={this.state.filename}
          filenames={this.state.filenames}
          changeFile={this.changeFile}
          saveCode={this.saveCode}
        />
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
