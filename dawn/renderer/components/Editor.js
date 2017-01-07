import React from 'react';
import ConsoleOutput from './ConsoleOutput';
import {
  Panel,
  Button,
  ButtonGroup,
  ButtonToolbar,
  DropdownButton,
  MenuItem,
  Glyphicon,
  OverlayTrigger,
  Tooltip,
  Row,
  Col,
} from 'react-bootstrap';
import AceEditor from 'react-ace';
import _ from 'lodash';
import storage from 'electron-json-storage';
import { remote } from 'electron';

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
    this.state = { editorHeight: this.getEditorHeight() };
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
          // 'res' is an integer corrseponding to index in button list above.
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
    });
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
    console.log('Deprecated: sendCode');
    console.log(`Debug Info: ${command} EOD`);
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
    console.log('Deprecated');
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

  renderTooltip(text, button) {
    const tooltip = (
      <Tooltip id="tooltip">{text}</Tooltip>
    );
    return (
      <OverlayTrigger placement="top" overlay={tooltip}>
        {button}
      </OverlayTrigger>
    );
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
          </Row>
        }
      >
        <ButtonToolbar>
          <ButtonGroup>
            {this.renderTooltip('Run',
              <Button
                bsStyle="default"
                bsSize="small"
                onClick={this.startRobot}
                disabled={this.props.isRunningCode || !this.props.runtimeStatus}
              >
                <Glyphicon glyph="play" />
              </Button>
            )}
            {this.renderTooltip('Stop',
              <Button
                bsStyle="default"
                bsSize="small"
                onClick={this.stopRobot}
                disabled={!(this.props.isRunningCode && this.props.runtimeStatus)}
              >
                <Glyphicon glyph="stop" />
              </Button>
            )}
            {this.renderTooltip('Upload',
              <Button
                bsStyle="default"
                bsSize="small"
                onClick={this.upload}
                disabled={this.props.isRunningCode || !this.props.runtimeStatus}
              >
                <Glyphicon glyph="upload" />
              </Button>
            )}
          </ButtonGroup>
          <ButtonGroup>
            {this.renderTooltip('Toggle Console',
              <Button
                bsStyle="default"
                bsSize="small"
                onClick={this.toggleConsole}
              >
                <Glyphicon glyph="console" />
              </Button>
            )}
            {this.renderTooltip('Clear Console',
              <Button
                bsStyle="default"
                bsSize="small"
                onClick={this.props.onClearConsole}
              >
                <Glyphicon glyph="remove" />
              </Button>
            )}
          </ButtonGroup>
          <ButtonGroup>
            {this.renderTooltip('API Documentation',
              <Button
                bsStyle="default"
                bsSize="small"
                onClick={this.openAPI}
              >
                <Glyphicon glyph="book" />
              </Button>
            )}
            {this.renderTooltip('Increase fontsize',
              <Button
                bsStyle="default"
                bsSize="small"
                onClick={this.increaseFontsize}
                disabled={this.props.fontSize > 28}
              >
                <Glyphicon glyph="zoom-in" />
              </Button>
            )}
            {this.renderTooltip('Decrease fontsize',
              <Button
                bsStyle="default"
                bsSize="small"
                onClick={this.decreaseFontsize}
                disabled={this.props.fontSize < 8}
              >
                <Glyphicon glyph="zoom-out" />
              </Button>
            )}
          </ButtonGroup>
          <ButtonGroup>
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
          </ButtonGroup>
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
  onChangeTheme: React.PropTypes.func,
  onChangeFontsize: React.PropTypes.func,
  onShowConsole: React.PropTypes.func,
  onHideConsole: React.PropTypes.func,
  onClearConsole: React.PropTypes.func,
  isRunningCode: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
};

export default Editor;
