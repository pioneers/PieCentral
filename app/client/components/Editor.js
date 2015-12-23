import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import EditorActionCreators from '../actions/EditorActionCreators';
import EditorStore from '../stores/EditorStore';
import EditorToolbar from './EditorToolbar';
import Mousetrap from 'mousetrap';
import 'brace/mode/python';
import 'brace/theme/monokai';
import ConsoleOutput from './ConsoleOutput';
import RemoteRobotStore from '../stores/RemoteRobotStore';
import RobotActions from '../actions/RobotActions';
import AnsibleClient from '../utils/AnsibleClient';
import _ from 'lodash';

var Editor = React.createClass({
  getInitialState() {
    var initState = {
      showConsole: false,
      consoleOutput: [],
      status: false,
      connection: true
    };
    _.merge(initState, EditorStore.getEditorData());
    return initState;
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
    RemoteRobotStore.on('change', this.updateRemoteRobotData);
    EditorStore.on('error', this.alertError);
    EditorActionCreators.getCode(this.state.filename);
  },
  componentWillUnmount() {
    Mousetrap.unbind(['mod+s']);
    EditorStore.removeListener('change', this.updateEditorData);
    RemoteRobotStore.removeListener('change', this.updateRemoteRobotData);
    EditorStore.removeListener('error', this.alertError);
  },
  updateEditorData() {
    this.setState(EditorStore.getEditorData());
  },
  updateRemoteRobotData() {
    this.setState({
      consoleOutput: RemoteRobotStore.getConsoleData(),
      status: RemoteRobotStore.getRobotStatus(),
      connection: RemoteRobotStore.getConnectionStatus()
    });
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
  toggleConsole() {
    this.setState({showConsole: !this.state.showConsole});
    // must call resize method after changing height of ace editor
    setTimeout(()=>this.refs.CodeEditor.editor.resize(), 0.1);
  },
  clearConsole() {
    RobotActions.clearConsole();
  },
  startRobot() {
    AnsibleClient.sendMessage('execute', {});
  },
  stopRobot() {
    AnsibleClient.sendMessage('stop', {});
  },
  render() {
    var unsavedChanges = (this.state.latestSaveCode !== this.state.editorCode);
    var consoleHeight = 250;
    return (
      <div>
        <EditorToolbar
          unsavedChanges={unsavedChanges}
          filename={this.state.filename}
          filenames={this.state.filenames}
          changeFile={this.changeFile}
          saveCode={this.saveCode}
          toggleConsole={this.toggleConsole}
          clearConsole={this.clearConsole}
          startRobot={this.startRobot}
          stopRobot={this.stopRobot}
          status={this.state.status}
          connection={this.state.connection}
        />
        <AceEditor
          mode="python"
          theme="monokai"
          width="100%"
          ref="CodeEditor"
          name="CodeEditor"
          height={String(500 - this.state.showConsole * consoleHeight) + 'px'}
          value = { this.state.editorCode }
          onChange={ this.editorUpdate }
          editorProps={{$blockScrolling: Infinity}}
        />
        <ConsoleOutput
          show={this.state.showConsole}
          height={String(consoleHeight) + 'px'}
          output={this.state.consoleOutput}/>
      </div>
    );
  }
});

export default Editor;
