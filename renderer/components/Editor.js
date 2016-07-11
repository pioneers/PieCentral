import React from 'react';
import ConsoleOutput from './ConsoleOutput';
import Ansible from '../utils/Ansible';
import {
  Panel,
  Button,
  ButtonGroup,
  Glyphicon,
  Row,
  Col,
} from 'react-bootstrap';
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

  getEditorHeight(windowHeight) {
    return `${String(windowHeight - 135 - this.props.showConsole * (this.consoleHeight + 40))}px`;
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
    const changeMarker = this.hasUnsavedChanges() ? '*' : '';
    return (
      <Panel
        bsStyle="primary"
        header={
          <Row>
            <Col md={6}>
              Editing: {this.pathToName(this.props.filepath)} {changeMarker}
            </Col>
            <Col md={6}>
              <ButtonGroup className="pull-right">
                <Button
                  bsStyle="default"
                  bsSize="small"
                  onClick={this.startRobot}
                  disabled={this.props.isRunningCode || !this.props.runtimeStatus}
                >
                  <Glyphicon glyph="play" />
                </Button>
                <Button
                  bsStyle="default"
                  bsSize="small"
                  onClick={this.stopRobot}
                  disabled={!(this.props.isRunningCode && this.props.runtimeStatus)}
                >
                  <Glyphicon glyph="stop" />
                </Button>
                <Button
                  bsStyle="default"
                  bsSize="small"
                  onClick={this.upload}
                  disabled={this.props.isRunningCode || !this.props.runtimeStatus}
                >
                  <Glyphicon glyph="upload" />
                </Button>
              </ButtonGroup>
              <ButtonGroup className="pull-right">
                <Button
                  bsStyle="default"
                  bsSize="small"
                  onClick={this.toggleConsole}
                >
                  <Glyphicon glyph="console" />
                </Button>
                <Button
                  bsStyle="default"
                  bsSize="small"
                  onClick={this.props.onClearConsole}
                >
                  <Glyphicon glyph="remove" />
                </Button>
              </ButtonGroup>
            </Col>
          </Row>
        }
      >
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
  onChangeTheme: React.PropTypes.func,
  onIncreaseFontsize: React.PropTypes.func,
  onDecreaseFontsize: React.PropTypes.func,
  onShowConsole: React.PropTypes.func,
  onHideConsole: React.PropTypes.func,
  onClearConsole: React.PropTypes.func,
  isRunningCode: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
};

export default Editor;
