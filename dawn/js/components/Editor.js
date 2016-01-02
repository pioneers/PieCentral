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
      this.saveFile();
    });

    EditorStore.on('change', this.updateEditorData);
    RemoteRobotStore.on('change', this.updateRemoteRobotData);
    EditorStore.on('error', this.alertError);
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
  openFile() {
    EditorActionCreators.openFile();
  },
  saveFile() {
    EditorActionCreators.saveFile(this.state.filePath, this.state.editorCode);
  },
  editorUpdate(newVal) {
    EditorActionCreators.editorUpdate(newVal);
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
  generateButtons() {
    // The buttons which will be in the button toolbar
    return [
      [
        {
          name: 'open',
          text: 'Open',
          onClick: this.openFile,
          glyph: 'folder-open'
        },
        {
          name: 'save',
          text: 'Save',
          onClick: this.saveFile,
          glyph: 'floppy-disk'
        },
        {
          name: 'create',
          text: 'Create',
          onClick() {
            alert('test');
          },
          glyph: 'file'
        },
        {
          name: 'delete',
          text: 'Delete',
          onClick() {
            alert('test');
          },
          glyph: 'trash'
        }
      ],
      [
        {
          name: 'run',
          text: 'Run',
          onClick: this.startRobot,
          glyph: 'play',
          disabled: (this.state.status || !this.state.connection)
        },
        {
          name: 'stop',
          text: 'Stop',
          onClick: this.stopRobot,
          glyph: 'stop',
          disabled: !(this.state.status && this.state.connection)
        },
        {
          name: 'toggle-console',
          text: 'Toggle Console',
          onClick: this.toggleConsole,
          glyph: 'console'
        },
        {
          name: 'clear-console',
          text: 'Clear Console',
          onClick: this.clearConsole,
          glyph: 'remove'
        }
      ]
    ];
  },
  render() {
    var unsavedChanges = (this.state.latestSaveCode !== this.state.editorCode);
    var consoleHeight = 250;
    return (
      <div>
        <EditorToolbar
          currentFilePath={this.state.filePath}
          buttons={this.generateButtons()}
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
