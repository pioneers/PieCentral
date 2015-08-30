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
    EditorActionCreators.getCode('student_code.py');
    EditorStore.on('change', this.updateEditor);
  },
  componentWillUnmount() {
    EditorStore.removeListener('change', this.updateEditor);
  },
  saveCode() {
    var currentVal = this.refs.CodeEditor.editor.getValue();
    EditorActionCreators.sendCode('student_code.py', currentVal);
  },
  render() {
    return (
      <Panel header="Code Editor" bsStyle="primary">
        <ButtonToolbar>
          <Button bsSize="small" bsStyle='default' onClick={this.saveCode}>Save</Button>
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
