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
import {dialog} from 'electron';

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
          name: 'Open',
          onClick() {
            alert('test');
          },
          glyph: 'folder-open'
        },
        {
          name: 'Save',
          onClick() {
            alert('test');
          },
          glyph: 'floppy-disk'
        },
        {
          name: 'Create',
          onClick() {
            alert('test');
          },
          glyph: 'file'
        },
        {
          name: 'Delete',
          onClick() {
            alert('test');
          },
          glyph: 'trash'
        }
      ],
      [
        {
          name: 'Run',
          onClick: this.startRobot,
          glyph: 'play'
        },
        {
          name: 'Stop',
          onClick: this.stopRobot,
          glyph: 'stop'
        },
        {
          name: 'Toggle Console',
          onClick() {
            alert('test');
          },
          glyph: 'console'
        },
        {
          name: 'Clear Console',
          onClick() {
            alert('test');
          },
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
