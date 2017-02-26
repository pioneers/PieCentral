import React from 'react';
import {
  Panel,
  ButtonGroup,
  ButtonToolbar,
  DropdownButton,
  MenuItem,
} from 'react-bootstrap';
import AceEditor from 'react-ace';
import _ from 'lodash';
import storage from 'electron-json-storage';
import { remote, ipcRenderer } from 'electron';

// React-ace extensions and modes
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

import UpdateBox from './UpdateBox';
import ConfigBox from './ConfigBox';
import ConsoleOutput from './ConsoleOutput';
import EditorButton from './EditorButton';
import { pathToName } from '../utils/utils';

const Client = require('ssh2').Client;

const dialog = remote.dialog;
const currentWindow = remote.getCurrentWindow();

class Editor extends React.Component {
  constructor(props) {
    super(props);
    this.consoleHeight = 250; // pixels
    this.themes = [
      'monokai',
      'github',
      'tomorrow',
      'kuroir',
      'twilight',
      'xcode',
      'textmate',
      'solarized_dark',
      'solarized_light',
      'terminal',
    ];
    this.toggleConsole = this.toggleConsole.bind(this);
    this.getEditorHeight = this.getEditorHeight.bind(this);
    this.changeTheme = this.changeTheme.bind(this);
    this.increaseFontsize = this.increaseFontsize.bind(this);
    this.decreaseFontsize = this.decreaseFontsize.bind(this);
    this.toggleUpdateModal = this.toggleUpdateModal.bind(this);
    this.toggleConfigModal = this.toggleConfigModal.bind(this);
    this.startRobot = this.startRobot.bind(this);
    this.stopRobot = this.stopRobot.bind(this);
    this.upload = this.upload.bind(this);
    this.toggleUpdateModal = this.toggleUpdateModal.bind(this);
    this.toggleConfigModal = this.toggleConfigModal.bind(this);
    this.estop = this.estop.bind(this);
    this.state = {
      editorHeight: this.getEditorHeight(),
      showUpdateModal: false,
      showConfigModal: false,
    };
  }

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
          message: 'You are trying to exit Dawn, but you have unsaved changes. ' +
          'What do you want to do with your unsaved changes?',
        }, (res) => {
          // 'res' is an integer corresponding to index in button list above.
          if (res === 0) {
            this.props.onSaveFile();
            window.onbeforeunload = null;
            currentWindow.close();
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

    storage.get('editorTheme', (err, data) => {
      if (err) throw err;
      if (!_.isEmpty(data)) this.props.onChangeTheme(data.theme);
    });

    storage.get('editorFontSize', (err, data) => {
      if (err) throw err;
      if (!_.isEmpty(data)) this.props.onChangeFontsize(data.editorFontSize);
    });

    // Trigger editor to re-render with window resize
    window.addEventListener('resize', () => {
      this.setState({ editorHeight: this.getEditorHeight() });
    }, { passive: true });
  }

  shouldComponentUpdate(nextProps, nextState) {
    return nextProps !== this.props || nextState !== this.state;
  }

  onEditorPaste(pasteData) {
    // Must correct non-ASCII characters, which would crash Runtime.
    let correctedText = pasteData.text;
    // Normalizing will allow us (in some cases) to preserve ASCII equivalents.
    correctedText = correctedText.normalize('NFD');
    // Special case to replace fancy quotes.
    correctedText = correctedText.replace(/[”“]/g, '"');
    correctedText = correctedText.replace(/[‘’]/g, "'");
    correctedText = this.correctText(correctedText);
    // TODO: Create some notification that an attempt was made at correcting non-ASCII chars.
    pasteData.text = correctedText; // eslint-disable-line no-param-reassign
  }

  getEditorHeight(windowHeight) {
    return `${String(windowHeight - 160 - (this.props.showConsole * (this.consoleHeight + 40)))}px`;
  }

  correctText(text) {
    // Removes non-ASCII characters from text.
    return text.replace(/[^\x00-\x7F]/g, ''); // eslint-disable-line no-control-regex
  }

  toggleConsole() {
    if (this.props.showConsole) {
      this.props.onHideConsole();
    } else {
      this.props.onShowConsole();
    }
    // must call resize method after changing height of ace editor
    setTimeout(() => this.refs.CodeEditor.editor.resize(), 0.1);
  }

  upload() {
    const filepath = this.props.filepath;
    if (filepath == null) {
      dialog.showMessageBox({
        type: 'warning',
        buttons: ['Close'],
        title: 'No Files',
        message: 'No file? No upload',
      });
      console.log('No file? No upload');
      return;
    }
    const correctedText = this.correctText(this.props.editorCode);
    if (correctedText !== this.props.editorCode) {
      this.props.onAlertAdd(
        'Invalid characters detected',
        'Your code has non-ASCII characters, which won\'t work on the robot. ' +
        'Please remove them and try again.',
      );
      return;
    }
    const conn = new Client();
    conn.on('error', (err) => {
      dialog.showMessageBox({
        type: 'warning',
        buttons: ['Close'],
        title: 'Connection Issue',
        message: 'Could Not Connect to Robot',
      });
      throw err;
    });
    ipcRenderer.send('NOTIFY_UPLOAD');
    while (this.notificationHold === 1) {

    }
    if (this.notificationHold === 2) {
      conn.end();
      this.onNotifyChange(0);
      this.props.onAlertAdd(
        'TCP ERROR',
        'No Reply Back from Runtime',
      );
      return;
    }
    conn.on('ready', () => {
      conn.sftp((err, sftp) => {
        if (err) {
          dialog.showMessageBox({
            type: 'warning',
            buttons: ['Close'],
            title: 'Connection Issue',
            message: 'Could Not Connect to Robot',
          });
          throw err;
        }
        console.log('SSH Connection');
        sftp.fastPut(filepath, './studentcode/studentcode.py', (err2) => {
          if (err2) {
            dialog.showMessageBox({
              type: 'warning',
              buttons: ['Close'],
              title: 'Upload Issue',
              message: 'Code Upload Failed.',
            });
            throw err2;
          }
        });
      });
    }).connect({
      debug: (inpt) => { console.log(inpt); },
      host: this.props.ipAddress,
      port: this.props.port,
      username: this.props.username,
      password: this.props.password,
    });
    setTimeout(() => { conn.end(); }, 2000);
  }

  startRobot() {
    this.props.onUpdateCodeStatus(1);
    this.props.onClearConsole();
  }

  stopRobot() {
    this.props.onUpdateCodeStatus(0);
  }

  toggleUpdateModal() {
    this.setState({ showUpdateModal: !this.state.showUpdateModal });
  }

  toggleConfigModal() {
    this.setState({ showConfigModal: !this.state.showConfigModal });
  }

  estop() {
    this.props.onUpdateCodeStatus(3);
  }

  hasUnsavedChanges() {
    return (this.props.latestSaveCode !== this.props.editorCode);
  }

  changeTheme(theme) {
    this.props.onChangeTheme(theme);
    storage.set('editorTheme', { theme }, (err) => {
      if (err) throw err;
    });
  }

  increaseFontsize() {
    this.props.onChangeFontsize(this.props.fontSize + 1);
    storage.set('editorFontSize', { editorFontSize: this.props.fontSize + 1 }, (err) => {
      if (err) throw err;
    });
  }

  decreaseFontsize() {
    this.props.onChangeFontsize(this.props.fontSize - 1);
    storage.set('editorFontSize', { editorFontSize: this.props.fontSize - 1 }, (err) => {
      if (err) throw err;
    });
  }

  render() {
    const changeMarker = this.hasUnsavedChanges() ? '*' : '';
    return (
      <Panel
        bsStyle="primary"
        header={
          <span style={{ fontSize: '14px' }}>
            Editing: {pathToName(this.props.filepath) ? pathToName(this.props.filepath) : '[ New File ]' } {changeMarker}
          </span>
        }
      >
        <UpdateBox
          isRunningCode={this.props.isRunningCode}
          connectionStatus={this.props.connectionStatus}
          runtimeStatus={this.props.runtimeStatus}
          shouldShow={this.state.showUpdateModal}
          ipAddress={this.props.ipAddress}
          port={this.props.port}
          username={this.props.username}
          password={this.props.password}
          hide={this.toggleUpdateModal}
        />
        <ConfigBox
          isRunningCode={this.props.isRunningCode}
          connectionStatus={this.props.connectionStatus}
          runtimeStatus={this.props.runtimeStatus}
          shouldShow={this.state.showConfigModal}
          ipAddress={this.props.ipAddress}
          onIPChange={this.props.onIPChange}
          hide={this.toggleConfigModal}
        />
        <ButtonToolbar>
          <ButtonGroup id="file-operations-buttons">
            <EditorButton
              text="New"
              onClick={this.props.onCreateNewFile}
              glyph="file"
            />
            <EditorButton
              text="Open"
              onClick={this.props.onOpenFile}
              glyph="folder-open"
            />
            <EditorButton
              text="Save"
              onClick={this.props.onSaveFile}
              glyph="floppy-disk"
            />
            <EditorButton
              text="Save As"
              onClick={_.partial(this.props.onSaveFile, true)}
              glyph="floppy-save"
            />
          </ButtonGroup>
          <ButtonGroup id="code-execution-buttons">
            <EditorButton
              text="Run"
              onClick={this.startRobot}
              glyph="play"
              disabled={this.props.isRunningCode || !this.props.runtimeStatus}
            />
            <EditorButton
              text="Stop"
              onClick={this.stopRobot}
              glyph="stop"
              disabled={!(this.props.isRunningCode && this.props.runtimeStatus)}
            />
            <EditorButton
              text="Upload"
              onClick={this.upload}
              glyph="upload"
              // disabled={this.props.isRunningCode || !this.props.runtimeStatus}
            />
          </ButtonGroup>
          <ButtonGroup id="console-buttons">
            <EditorButton
              text="Toggle Console"
              onClick={this.toggleConsole}
              glyph="console"
            />
            <EditorButton
              text="Clear Console"
              onClick={this.onClearConsole}
              glyph="remove"
            />
          </ButtonGroup>
          <ButtonGroup id="misc-buttons">
            <EditorButton
              text="E-STOP"
              onClick={this.estop}
              glyph="fire"
            />
            <EditorButton
              text="Increase font size"
              onClick={this.increaseFontsize}
              glyph="zoom-in"
              disabled={this.props.fontSize > 28}
            />
            <EditorButton
              text="Decrease font size"
              onClick={this.decreaseFontsize}
              glyph="zoom-out"
              disabled={this.props.fontSize < 7}
            />
            <EditorButton
              text="Updates"
              onClick={this.toggleUpdateModal}
              glyph="cloud-upload"
            />
            <EditorButton
              text="Configuration"
              onClick={this.toggleConfigModal}
              glyph="cog"
            />
          </ButtonGroup>
          <DropdownButton
            title="Theme"
            bsSize="small"
            id="choose-theme"
          >
            {_.map(this.themes, (theme, index) => (
              <MenuItem
                active={theme === this.props.editorTheme}
                onClick={_.partial(this.changeTheme, theme)}
                key={index}
              >
                {theme}
              </MenuItem>
            ))}
          </DropdownButton>
        </ButtonToolbar>
        <AceEditor
          mode="python"
          theme={this.props.editorTheme}
          width="100%"
          fontSize={this.props.fontSize}
          ref="CodeEditor"
          name="CodeEditor"
          height={this.getEditorHeight(window.innerHeight)}
          value={this.props.editorCode}
          onChange={this.props.onEditorUpdate}
          onPaste={this.onEditorPaste}
          editorProps={{ $blockScrolling: Infinity }}
        />
        <ConsoleOutput
          toggleConsole={this.toggleConsole}
          show={this.props.showConsole}
          height={this.consoleHeight}
          output={this.props.consoleData}
        />
      </Panel>
    );
  }
}

Editor.propTypes = {
  editorCode: React.PropTypes.string,
  editorTheme: React.PropTypes.string,
  filepath: React.PropTypes.string,
  fontSize: React.PropTypes.number,
  latestSaveCode: React.PropTypes.string,
  showConsole: React.PropTypes.bool,
  consoleData: React.PropTypes.array,
  onAlertAdd: React.PropTypes.func,
  onEditorUpdate: React.PropTypes.func,
  onSaveFile: React.PropTypes.func,
  onOpenFile: React.PropTypes.func,
  onCreateNewFile: React.PropTypes.func,
  onChangeTheme: React.PropTypes.func,
  onChangeFontsize: React.PropTypes.func,
  onShowConsole: React.PropTypes.func,
  onHideConsole: React.PropTypes.func,
  onClearConsole: React.PropTypes.func,
  onUpdateCodeStatus: React.PropTypes.func,
  onIPChange: React.PropTypes.func,
  isRunningCode: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  connectionStatus: React.PropTypes.bool,
  ipAddress: React.PropTypes.string,
  port: React.PropTypes.number,
  username: React.PropTypes.string,
  password: React.PropTypes.string,
  notificationHold: React.PropTypes.number,
  onNotifyChange: React.PropTypes.func,
};

export default Editor;
