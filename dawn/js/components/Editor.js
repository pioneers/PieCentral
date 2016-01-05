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
import RobotActions from '../actions/RobotActions';
import Ansible from '../utils/Ansible';
import {Panel} from 'react-bootstrap';

export default React.createClass({
  getInitialState() {
    return {
      showConsole: false,
      filepath: null,
      latestSaveCode: '',
      editorCode: ''
    };
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
  },
  componentWillUnmount() {
    Mousetrap.unbind(['mod+s']);
    EditorStore.removeListener('change', this.updateEditorData);
  },
  updateEditorData() {
    this.setState({
      filepath: EditorStore.getFilepath(),
      latestSaveCode: EditorStore.getLatestSaveCode(),
      editorCode: EditorStore.getEditorCode()
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
    Ansible.sendMessage('execute', {
      code: this.state.editorCode
    });
  },
  stopRobot() {
    Ansible.sendMessage('stop', {});
  },
  generateButtons() {
    // The buttons which will be in the button toolbar
    return [
      {
        groupId: 'file-operations-buttons',
        buttons:
        [
          {
            name: 'save',
            text: 'Save',
            onClick: this.saveFile,
            glyph: 'floppy-disk'
          },
          {
            name: 'open',
            text: 'Open',
            onClick: this.openFile,
            glyph: 'folder-open'
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
      }, {
        groupId: 'code-execution-buttons',
        buttons:
        [
          {
            name: 'run',
            text: 'Run',
            onClick: this.startRobot,
            glyph: 'play',
            disabled: (this.props.isRunningCode || !this.props.connectionStatus )
          },
          {
            name: 'stop',
            text: 'Stop',
            onClick: this.stopRobot,
            glyph: 'stop',
            disabled: !(this.props.isRunningCode && this.props.connectionStatus)
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
      }
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
    let editorHeight = 530;
    return (
      <Panel
        header={'Editing: ' + this.pathToName(this.state.filepath) +
          (this.hasUnsavedChanges() ? '*' : '')}
        bsStyle="primary">
        <EditorToolbar
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
          output={this.props.consoleData}/>
      </Panel>
    );
  }
});
