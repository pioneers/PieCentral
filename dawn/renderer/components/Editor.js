import React from 'react';
import { connect } from 'react-redux';
import {
  changeTheme,
  editorUpdate,
  increaseFontsize,
  decreaseFontsize,
} from '../actions/EditorActions.js';
import {
  showConsole,
  hideConsole,
  clearConsole,
} from '../actions/ConsoleActions';
import { addAsyncAlert } from '../actions/AlertActions';
import EditorToolbar from './EditorToolbar';
import ConsoleOutput from './ConsoleOutput';
import Ansible from '../utils/Ansible';
import { Panel } from 'react-bootstrap';
import { EditorButton } from './EditorClasses';
import AceEditor from 'react-ace';

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

class EditorComponent extends React.Component {
  constructor(props) {
    super(props);
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
  }

  componentDidMount() {
    this.refs.CodeEditor.editor.setOption('enableBasicAutocompletion', true);
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

  sendCode(command) {
    const correctedText = this.correctText(this.props.editorCode);
    if (correctedText !== this.props.editorCode) {
      this.props.onAlertAdd(
        'Invalid characters detected',
        'Your code has non-ASCII characters, which won\'t work on the robot. ' +
        'Please remove them and try again.'
      );
      return false;
    }
    Ansible.sendMessage(command, {
      code: this.props.editorCode,
    });
    return true;
  }

  upload() {
    this.sendCode('upload');
  }

  startRobot() {
    const sent = this.sendCode('execute');
    if (sent) {
      this.props.onClearConsole();
    }
  }

  stopRobot() {
    Ansible.sendMessage('stop', {});
  }

  openAPI() {
    window.open('https://pie-api.readthedocs.org/');
  }

  generateButtons() {
    // The buttons which will be in the button toolbar
    return [
      {
        groupId: 'code-execution-buttons',
        buttons: [
          new EditorButton(
            'run',
            'Run',
            this.startRobot,
            'play',
            (this.props.isRunningCode || !this.props.runtimeStatus)
          ),
          new EditorButton(
            'stop',
            'Stop',
            this.stopRobot,
            'stop',
            !(this.props.isRunningCode && this.props.runtimeStatus)
          ),
          new EditorButton('toggle-console', 'Toggle Console', this.toggleConsole, 'console'),
          new EditorButton('clear-console', 'Clear Console', this.props.onClearConsole, 'remove'),
          new EditorButton(
            'upload',
            'Upload',
            this.upload,
            'upload',
            (this.props.isRunningCode || !this.props.runtimeStatus)
          ),
        ],
      }, {
        groupId: 'misc-buttons',
        buttons: [
          new EditorButton('api', 'API Documentation', this.openAPI, 'book'),
          new EditorButton('zoomin', 'Increase fontsize', this.props.onIncreaseFontsize, 'zoom-in'),
          new EditorButton(
            'zoomout',
            'Decrease fontsize',
            this.props.onDecreaseFontsize,
            'zoom-out'
          ),
        ],
      },
    ];
  }

  pathToName(filepath) {
    if (filepath !== null) {
      if (process.platform === 'win32') {
        return filepath.split('\\').pop();
      }
      return filepath.split('/').pop();
    }
    return '[ New File ]';
  }

  hasUnsavedChanges() {
    return (this.props.latestSaveCode !== this.props.editorCode);
  }

  render() {
    const consoleHeight = 250;
    const editorHeight = window.innerHeight * 0.66;
    const changeMarker = this.hasUnsavedChanges() ? '*' : '';
    return (
      <Panel
        header={`Editing: ${this.pathToName(this.props.filepath)}${changeMarker}`}
        bsStyle="primary"
      >
        <EditorToolbar
          buttons={this.generateButtons()}
          unsavedChanges={this.hasUnsavedChanges()}
          changeTheme={this.props.onChangeTheme}
          editorTheme={this.props.editorTheme}
          themes={this.themes}
          runtimeStatus={this.props.runtimeStatus}
        />
        <AceEditor
          mode="python"
          theme={this.props.editorTheme}
          width="100%"
          fontSize={this.props.fontSize}
          ref="CodeEditor"
          name="CodeEditor"
          height={`${String(editorHeight - this.props.showConsole * (consoleHeight + 30))}px`}
          value={this.props.editorCode}
          onChange={this.props.onEditorUpdate}
          onPaste={this.onEditorPaste}
          editorProps={{ $blockScrolling: Infinity }}
        />
        <ConsoleOutput
          toggleConsole={this.toggleConsole}
          show={this.props.showConsole}
          height={consoleHeight}
          output={this.props.consoleData}
        />
      </Panel>
    );
  }
}

EditorComponent.propTypes = {
  editorCode: React.PropTypes.string,
  editorTheme: React.PropTypes.string,
  filepath: React.PropTypes.string,
  fontSize: React.PropTypes.number,
  latestSaveCode: React.PropTypes.string,
  showConsole: React.PropTypes.bool,
  consoleData: React.PropTypes.array,
  onAlertAdd: React.PropTypes.func,
  onEditorUpdate: React.PropTypes.func,
  onChangeTheme: React.PropTypes.func,
  onIncreaseFontsize: React.PropTypes.func,
  onDecreaseFontsize: React.PropTypes.func,
  onShowConsole: React.PropTypes.func,
  onHideConsole: React.PropTypes.func,
  onClearConsole: React.PropTypes.func,
  isRunningCode: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
};

const mapStateToProps = (state) => ({
  editorCode: state.editor.editorCode,
  editorTheme: state.editor.editorTheme,
  filepath: state.editor.filepath,
  fontSize: state.editor.fontSize,
  latestSaveCode: state.editor.latestSaveCode,
  showConsole: state.studentConsole.showConsole,
  consoleData: state.studentConsole.consoleData,
});

const mapDispatchToProps = (dispatch) => ({
  onAlertAdd: (heading, message) => {
    dispatch(addAsyncAlert(heading, message));
  },
  onEditorUpdate: (newVal) => {
    dispatch(editorUpdate(newVal));
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
  onShowConsole: () => {
    dispatch(showConsole());
  },
  onHideConsole: () => {
    dispatch(hideConsole());
  },
  onClearConsole: () => {
    dispatch(clearConsole());
  },
});

const Editor = connect(mapStateToProps, mapDispatchToProps)(EditorComponent);
export default Editor;
