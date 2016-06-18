import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import {
  openFile,
  saveFile,
  deleteFile,
  createNewFile,
  changeTheme,
  editorUpdate,
  increaseFontsize,
  decreaseFontsize
} from '../actions/EditorActions.js';
import {
  showConsole,
  hideConsole,
  clearConsole
} from '../actions/ConsoleActions';
import { connect } from 'react-redux';
import { addAsyncAlert } from '../actions/AlertActions';
import EditorToolbar from './EditorToolbar';
import Mousetrap from 'mousetrap';
import _ from 'lodash';
import ConsoleOutput from './ConsoleOutput';
import Ansible from '../utils/Ansible';
import { Panel } from 'react-bootstrap';
import { EditorButton } from './EditorClasses';
import ace from 'brace';
import 'brace/ext/language_tools';
import 'brace/ext/searchbox';
import 'brace/mode/python';
// React-ace themes
import 'brace/theme/monokai';
import 'brace/theme/github';
import 'brace/theme/tomorrow';
import 'brace/theme/kuroir';
import 'brace/theme/twilight';
import 'brace/theme/xcode';
import 'brace/theme/textmate';
import 'brace/theme/solarized_dark';
import 'brace/theme/solarized_light';
import 'brace/theme/terminal';
import { remote } from 'electron';
let langtools = ace.acequire('ace/ext/language_tools');
let storage = remote.require('electron-json-storage');
let dialog = remote.dialog;
let currentWindow = remote.getCurrentWindow();

let Editor = React.createClass({
  componentDidMount() {
    // If there are unsaved changes and the user tries to close Dawn,
    // check if they want to save their changes first.
    window.onbeforeunload = (e) => {
      if (this.hasUnsavedChanges()) {
        e.returnValue = false;
        dialog.showMessageBox({
          type: 'warning',
          buttons: ['Save and exit', 'Quit without saving', 'Cancel exit'],
          title: 'You have unsaved changes!',
          message: 'You are trying to exit Dawn, but you have unsaved changes. What do you want to do with your unsaved changes?'
        }, (res)=>{
          // 'res' is an integer corrseponding to index in button list above.
          if (res === 0) {
            this.saveFile(()=>{
              window.onbeforeunload = null;
              currentWindow.close();
            });
          } else if (res === 1) {
            window.onbeforeunload = null;
            currentWindow.close();
          } else {
            console.log('Exit canceled.');
          }
        });
      }
    };

    this.refs.CodeEditor.editor.setOption('enableBasicAutocompletion', true);

    Mousetrap.prototype.stopCallback = function(e, element, combo) {
      return false; // Always respond to keyboard combos
    };

    Mousetrap.bind(['mod+s'], (e)=>{
      if (e.preventDefault) {
        e.preventDefault();
      }
      this.saveFile();
    });
  },
  componentWillUnmount() {
    Mousetrap.unbind(['mod+s']);
  },
  openFile() {
    if (this.hasUnsavedChanges()) {
      dialog.showMessageBox({
        type: 'warning',
        buttons: ['Save and open', 'Discard and open', 'Cancel action'],
        title: 'You have unsaved changes!',
        message: 'You are trying to open a new file, but you have unsaved changes to your current one. What do you want to do?'
      }, (res)=>{
        // 'res' is an integer corrseponding to index in button list above.
        if (res === 0) {
          this.saveFile(()=>{
            process.nextTick(()=>{
              this.props.onOpenFile();
            });
          });
        } else if (res === 1) {
          this.props.onOpenFile();
        } else {
          console.log('File open canceled.');
        }
      });
    } else {
      this.props.onOpenFile();
    }
  },
  saveFile(callback) {
    this.props.onSaveFile(this.props.filepath, this.props.editorCode, callback);
  },
  saveAsFile() {
    this.props.onSaveFile(null, this.props.editorCode);
  },
  createNewFile() {
    if (this.hasUnsavedChanges()) {
      dialog.showMessageBox({
        type: 'warning',
        buttons: ['Save and create', 'Discard and create', 'Cancel action'],
        title: 'You have unsaved changes!',
        message: 'You are trying to create a new file, but you have unsaved changes to your current one. What do you want to do?'
      }, (res)=>{
        // 'res' is an integer corrseponding to index in button list above.
        if (res === 0) {
          this.saveFile(()=>{
            process.nextTick(()=>{
              this.props.onCreateNewFile();
            });
          });
        } else if (res === 1) {
          this.props.onCreateNewFile();
        } else {
          console.log('New file creation canceled.');
        }
      });
    } else {
      this.props.onCreateNewFile();
    }
  },
  correctText(text) {
    // Removes non-ASCII characters from text.
    return text.replace(/[^\x00-\x7F]/g, "");
  },
  onEditorPaste(pasteData) {
    // Must correct non-ASCII characters, which would crash Runtime.
    let correctedText = pasteData.text;
    // Normalizing will allow us (in some cases) to preserve ASCII equivalents.
    correctedText = correctedText.normalize("NFD");
    // Special case to replace fancy quotes.
    correctedText = correctedText.replace(/[”“]/g,'"');
    correctedText = correctedText.replace(/[‘’]/g,"'");
    correctedText = this.correctText(correctedText);
    // TODO: Create some notification that an attempt was made at correcting non-ASCII chars.
    pasteData.text = correctedText;
  },
  toggleConsole() {
    if (this.props.showConsole) {
      this.props.onHideConsole();
    } else {
      this.props.onShowConsole();
    }
    // must call resize method after changing height of ace editor
    setTimeout(()=>this.refs.CodeEditor.editor.resize(), 0.1);
  },
  sendCode(command) {
    let correctedText = this.correctText(this.props.editorCode);
    if (correctedText !== this.props.editorCode) {
      this.props.onAlertAdd(
	'Invalid characters detected',
	'Your code has non-ASCII characters, which won\'t work on the robot. ' +
	'Please remove them and try again.'
      );
      return false;
    } else {
      Ansible.sendMessage(command, {
	code: this.props.editorCode
      });
      return true;
    }
  },
  upload() { this.sendCode('upload'); },
  startRobot() {
    let sent = this.sendCode('execute');
    if (sent) {
      this.props.onClearConsole();
    };
  },
  stopRobot() {
    Ansible.sendMessage('stop', {});
  },
  openAPI() {
    window.open("https://pie-api.readthedocs.org/")
  },
  generateButtons() {
    // The buttons which will be in the button toolbar
    return [
      {
        groupId: 'file-operations-buttons',
        buttons: [
          new EditorButton('create', 'New', this.createNewFile, 'file'),
          new EditorButton('open', 'Open', this.openFile, 'folder-open'),
          new EditorButton('save', 'Save', this.saveFile, 'floppy-disk'),
          new EditorButton('saveas', 'Save As', this.saveAsFile, 'floppy-save')
        ],
      }, {
        groupId: 'code-execution-buttons',
        buttons: [
          new EditorButton('run', 'Run', this.startRobot, 'play', (this.props.isRunningCode || !this.props.runtimeStatus)),
          new EditorButton('stop', 'Stop', this.stopRobot, 'stop', !(this.props.isRunningCode && this.props.runtimeStatus)),
          new EditorButton('toggle-console', 'Toggle Console', this.toggleConsole, 'console'),
          new EditorButton('clear-console', 'Clear Console', this.props.onClearConsole, 'remove'),
          new EditorButton('upload', 'Upload', this.upload, 'upload', (this.props.isRunningCode || !this.props.runtimeStatus)),
        ]
      }, {
        groupId: 'misc-buttons',
        buttons: [
          new EditorButton('api', 'API Documentation', this.openAPI, 'book'),
          new EditorButton('zoomin', 'Increase fontsize', this.props.onIncreaseFontsize, 'zoom-in'),
          new EditorButton('zoomout', 'Decrease fontsize', this.props.onDecreaseFontsize, 'zoom-out')
        ]
      }
    ];
  },
  pathToName(filepath) {
    if (filepath !== null) {
      if (process.platform === 'win32') {
        return filepath.split('\\').pop();
      } else {
        return filepath.split('/').pop();
      }
    } else {
      return '[ New File ]';
    }
  },
  hasUnsavedChanges() {
    return (this.props.latestSaveCode !== this.props.editorCode);
  },
  themes: [
    'monokai',
    'github',
    'tomorrow',
    'kuroir',
    'twilight',
    'xcode',
    'textmate',
    'solarized_dark',
    'solarized_light',
    'terminal'
  ],
  render() {
    let consoleHeight = 250;
    let editorHeight = window.innerHeight * 0.66;
    return (
      <Panel
        header={'Editing: ' + this.pathToName(this.props.filepath) +
          (this.hasUnsavedChanges() ? '*' : '')}
        bsStyle="primary">
        <EditorToolbar
          buttons={ this.generateButtons() }
          unsavedChanges={ this.hasUnsavedChanges() }
          changeTheme={ this.props.onChangeTheme }
          editorTheme={ this.props.editorTheme }
          themes={ this.themes }
          runtimeStatus={ this.props.runtimeStatus }
        />
        <AceEditor
          mode="python"
          theme={ this.props.editorTheme }
          width="100%"
          fontSize={this.props.fontSize}
          ref="CodeEditor"
          name="CodeEditor"
          height={String(
            editorHeight - this.props.showConsole * (consoleHeight + 30)) + 'px'}
          value = { this.props.editorCode }
          onChange={ this.props.onEditorUpdate }
	  onPaste={ this.onEditorPaste }
          editorProps={{$blockScrolling: Infinity}}
        />
        <ConsoleOutput
          toggleConsole={this.toggleConsole}
          show={this.props.showConsole}
          height={consoleHeight}
          output={this.props.consoleData}/>
      </Panel>
    );
  }
});

const mapStateToProps = (state) => {
  return {
    editorCode: state.editor.editorCode,
    editorTheme: state.editor.editorTheme,
    filepath: state.editor.filepath,
    fontSize: state.editor.fontSize,
    latestSaveCode: state.editor.latestSaveCode,
    showConsole: state.studentConsole.showConsole,
    consoleData: state.studentConsole.consoleData
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    onAlertAdd: (heading, message) => {
      dispatch(addAsyncAlert(heading, message));
    },
    onEditorUpdate: (newVal) => {
      dispatch(editorUpdate(newVal));
    },
    onOpenFile: () => {
      dispatch(openFile());
    },
    onSaveFile: (filepath, code, callback) => {
      dispatch(saveFile(filepath, code, callback));
    },
    onChangeTheme: (theme) => {
      dispatch(changeTheme(theme));
    },
    onIncreaseFontsize: () => {
      dispatch(increaseFontsize());
    },
    onDecreaseFontsize: () => {
      dispatch(decreaseFontsize());
    },
    onCreateNewFile: () => {
      dispatch(createNewFile());
    },
    onShowConsole: () => {
      dispatch(showConsole());
    },
    onHideConsole: () => {
      dispatch(hideConsole());
    },
    onClearConsole: () => {
      dispatch(clearConsole());
    }
  };
};

Editor = connect(mapStateToProps, mapDispatchToProps)(Editor);
export default Editor;
