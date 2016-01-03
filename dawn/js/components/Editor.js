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

export default React.createClass({
  getInitialState() {
    let initState = {
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
  },
  componentWillUnmount() {
    Mousetrap.unbind(['mod+s']);
    EditorStore.removeListener('change', this.updateEditorData);
    RemoteRobotStore.removeListener('change', this.updateRemoteRobotData);
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
  openFile() {
    if (this.hasUnsavedChanges()) {
      alert('Please discard or save your current changes.')
    } else {
      EditorActionCreators.openFile();
    }
  },
  saveFile() {
    EditorActionCreators.saveFile(this.state.filepath, this.state.editorCode);
  },
  createNewFile() {
    if (this.hasUnsavedChanges()) {
      alert('Please discard or save your current changes.');
    } else {
      EditorActionCreators.createNewFile();
    }
  },
  deleteFile() {
    if(confirm('Warning: This will delete your file!')) {
      EditorActionCreators.deleteFile(this.state.filepath);
    }
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
          text: 'New',
          onClick: this.createNewFile,
          glyph: 'file'
        },
        {
          name: 'delete',
          text: 'Delete',
          onClick: this.deleteFile,
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
  pathToName(filepath) {
    if (filepath !== null) {
      return filepath.split('/').pop();
    } else {
      return '[ New File ]';
    }
  },
  hasUnsavedChanges() {
    return (this.state.latestSaveCode !== this.state.editorCode);
  },
  render() {
    let consoleHeight = 250;
    let editorHeight = 600;
    return (
      <div>
        <EditorToolbar
          currentFilename={ this.pathToName(this.state.filepath) }
          buttons={ this.generateButtons() }
          unsavedChanges={ this.hasUnsavedChanges() }
        />
        <AceEditor
          mode="python"
          theme="monokai"
          width="100%"
          ref="CodeEditor"
          name="CodeEditor"
          height={String(
            editorHeight - this.state.showConsole * (consoleHeight + 30)) + 'px'}
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
