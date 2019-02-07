import React from 'react';
import PropTypes from 'prop-types';
import {
  Panel,
  ButtonGroup,
  DropdownButton,
  MenuItem,
  FormGroup,
  FormControl,
  Form,
  InputGroup,
  OverlayTrigger,
  Tooltip,
} from 'react-bootstrap';
import AceEditor from 'react-ace';
import { remote, clipboard } from 'electron';
import storage from 'electron-json-storage';
import _ from 'lodash';


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

import ConsoleOutput from './ConsoleOutput';
import TooltipButton from './TooltipButton';
import { pathToName, robotState, defaults, timings, logging, windowInfo } from '../utils/utils';

const { dialog } = remote;
const currentWindow = remote.getCurrentWindow();

class Editor extends React.Component {
  /*
   * ASCII Enforcement
   */
  static onEditorPaste(pasteData) {
    let correctedText = pasteData.text;
    correctedText = correctedText.normalize('NFD');
    correctedText = correctedText.replace(/[”“]/g, '"');
    correctedText = correctedText.replace(/[‘’]/g, "'");
    correctedText = Editor.correctText(correctedText);
    // TODO: Create some notification that an attempt was made at correcting non-ASCII chars.
    pasteData.text = correctedText; // eslint-disable-line no-param-reassign
  }

  // TODO: Take onEditorPaste items and move to utils?
  static correctText(text) {
    return text.replace(/[^\x00-\x7F]/g, ''); // eslint-disable-line no-control-regex
  }

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
    this.beforeUnload = this.beforeUnload.bind(this);
    this.onWindowResize = this.onWindowResize.bind(this);
    this.toggleConsole = this.toggleConsole.bind(this);
    this.getEditorHeight = this.getEditorHeight.bind(this);
    this.changeTheme = this.changeTheme.bind(this);
    this.increaseFontsize = this.increaseFontsize.bind(this);
    this.decreaseFontsize = this.decreaseFontsize.bind(this);
    this.changeFontsizeToFont = this.changeFontsizeToFont.bind(this);
    this.handleSubmitFontsize = this.handleSubmitFontsize.bind(this);
    this.handleChangeFontsize = this.handleChangeFontsize.bind(this);
    this.startRobot = this.startRobot.bind(this);
    this.stopRobot = this.stopRobot.bind(this);
    this.upload = this.upload.bind(this);
    this.estop = this.estop.bind(this);
    this.simulateCompetition = this.simulateCompetition.bind(this);
    this.raiseConsole = this.raiseConsole.bind(this);
    this.lowerConsole = this.lowerConsole.bind(this);
    this.copyConsole = this.copyConsole.bind(this);
    this.state = {
      consoleHeight: windowInfo.CONSOLESTART,
      editorHeight: 0, // Filled in later during componentDidMount
      mode: robotState.TELEOP,
      modeDisplay: robotState.TELEOPSTR,
      simulate: false,
    };
  }

  /*
   * Confirmation Dialog on Quit, Stored Editor Settings, Window Size-Editor Re-render
   */
  componentDidMount() {
    this.CodeEditor.editor.setOptions({
      enableBasicAutocompletion: true,
      enableLiveAutocompletion: true,
    });
    const autoComplete = {
      getCompletions(editor, session, pos, prefix, callback) {
        callback(null, [
          { value: 'Robot', score: 1000, meta: 'PiE API' },
          { value: 'get_value', score: 900, meta: 'PiE API' },
          { value: 'set_value', score: 900, meta: 'PiE API' },
          { value: 'run', score: 900, meta: 'PiE API' },
          { value: 'is_running', score: 900, meta: 'PiE API' },
          { value: 'Gamepad', score: 1000, meta: 'PiE API' },
          { value: 'Actions', score: 1000, meta: 'PiE API' },
          { value: 'sleep', score: 900, meta: 'PiE API' },
          { value: '"button_a"', score: 900, meta: 'PiE API' },
          { value: '"button_b"', score: 900, meta: 'PiE API' },
          { value: '"button_x"', score: 900, meta: 'PiE API' },
          { value: '"button_y"', score: 900, meta: 'PiE API' },
          { value: '"l_bumper"', score: 900, meta: 'PiE API' },
          { value: '"r_bumper"', score: 900, meta: 'PiE API' },
          { value: '"l_trigger"', score: 900, meta: 'PiE API' },
          { value: '"r_trigger"', score: 900, meta: 'PiE API' },
          { value: '"button_back"', score: 900, meta: 'PiE API' },
          { value: '"button_start"', score: 900, meta: 'PiE API' },
          { value: '"l_stick"', score: 900, meta: 'PiE API' },
          { value: '"r_stick"', score: 900, meta: 'PiE API' },
          { value: '"dpad_up"', score: 900, meta: 'PiE API' },
          { value: '"dpad_down"', score: 900, meta: 'PiE API' },
          { value: '"dpad_left"', score: 900, meta: 'PiE API' },
          { value: '"dpad_right"', score: 900, meta: 'PiE API' },
          { value: '"button_xbox"', score: 900, meta: 'PiE API' },
          { value: 'def', score: 1000, meta: 'Python3' },
          { value: 'await', score: 1000, meta: 'Python3' },
          { value: 'print', score: 1000, meta: 'Python3' },
          { value: 'max', score: 1000, meta: 'Python3' },
          { value: 'min', score: 1000, meta: 'Python3' },
          { value: 'async', score: 1000, meta: 'Python3' },
          { value: 'lambda', score: 1000, meta: 'Python3' },
          { value: 'for', score: 1000, meta: 'Python3' },
          { value: 'while', score: 1000, meta: 'Python3' },
          { value: 'True', score: 1000, meta: 'Python3' },
          { value: 'False', score: 1000, meta: 'Python3' },
          { value: 'abs', score: 1000, meta: 'Python3' },
          { value: 'len', score: 1000, meta: 'Python3' },
          { value: 'round', score: 1000, meta: 'Python3' },
          { value: 'set()', score: 1000, meta: 'Python3' },
        ]);
      },
    };
    this.CodeEditor.editor.completers = [autoComplete];

    this.onWindowResize();
    storage.get('editorTheme', (err, data) => {
      if (err) {
        logging.log(err);
      } else if (!_.isEmpty(data)) {
        this.props.onChangeTheme(data.theme);
      }
    });

    storage.get('editorFontSize', (err, data) => {
      if (err) {
        logging.log(err);
      } else if (!_.isEmpty(data)) {
        this.props.onChangeFontsize(data.editorFontSize);
        this.setState({ fontsize: this.props.fontSize });
      }
    });


    window.addEventListener('beforeunload', this.beforeUnload);
    window.addEventListener('resize', this.onWindowResize, { passive: true });
    window.addEventListener('dragover', (e) => {
      e.preventDefault();
      return false;
    });
    window.addEventListener('drop', (e) => {
      e.preventDefault();
      this.props.onDragFile(e.dataTransfer.files[0].path);
      return false;
    });
  }

  componentWillUnmount() {
    window.removeEventListener('beforeunload', this.beforeUnload);
    window.removeEventListener('resize', this.onWindowResize);
  }

  onWindowResize() {
    // Trigger editor to re-render on window resizing.
    this.setState({ editorHeight: this.getEditorHeight() });
  }

  getEditorHeight() {
    const windowNonEditorHeight = windowInfo.NONEDITOR +
      (this.props.showConsole * (this.state.consoleHeight + windowInfo.CONSOLEPAD));
    return `${String(window.innerHeight - windowNonEditorHeight)}px`;
  }

  beforeUnload(event) {
    // If there are unsaved changes and the user tries to close Dawn,
    // check if they want to save their changes first.
    if (this.hasUnsavedChanges()) {
      const clickedId = dialog.showMessageBox(currentWindow, {
        type: 'warning',
        buttons: ['Save...', 'Don\'t Save', 'Cancel'],
        defaultId: 0,
        cancelId: 2,
        title: 'You have unsaved changes!',
        message: 'Do you want to save the changes made to your program?',
        detail: 'Your changes will be lost if you don\'t save them.',
      });

      // NOTE: For whatever reason, `event.preventDefault()` does not work within
      // beforeunload events, so we use `event.returnValue = false` instead.
      //
      // `clickedId` is the index of the clicked button in the button list above.
      if (clickedId === 0) {
        // FIXME: Figure out a way to make Save and Close, well, close.
        event.returnValue = false;
        this.props.onSaveFile();
      } else if (clickedId === 2) {
        event.returnValue = false;
      }
    }
  }

  toggleConsole() {
    this.props.toggleConsole();
    // Resize since the console overlaps with the editor, but enough time for console changes
    setTimeout(() => this.onWindowResize(), 0.01);
  }

  upload() {
    const { filepath } = this.props;
    if (filepath === '') {
      this.props.onAlertAdd(
        'Not Working on a File',
        'Please save first',
      );
      logging.log('Upload: Not Working on File');
      return;
    }
    if (this.hasUnsavedChanges()) {
      this.props.onAlertAdd(
        'Unsaved File',
        'Please save first',
      );
      logging.log('Upload: Not Working on Saved File');
      return;
    }
    if (Editor.correctText(this.props.editorCode) !== this.props.editorCode) {
      this.props.onAlertAdd(
        'Invalid characters detected',
        'Your code has non-ASCII characters, which won\'t work on the robot. ' +
        'Please remove them and try again.',
      );
      logging.log('Upload: Non-ASCII Issue');
      return;
    }

    this.props.onUploadCode();
  }

  startRobot() {
    this.props.onUpdateCodeStatus(this.state.mode);
    this.props.onClearConsole();
  }

  stopRobot() {
    this.setState({
      simulate: false,
      modeDisplay: (this.state.mode === robotState.AUTONOMOUS) ?
        robotState.AUTOSTR : robotState.TELEOPSTR,
    });
    this.props.onUpdateCodeStatus(robotState.IDLE);
  }

  estop() {
    this.setState({ simulate: false, modeDisplay: robotState.ESTOPSTR });
    this.props.onUpdateCodeStatus(robotState.ESTOP);
  }

  simulateCompetition() {
    this.setState({ simulate: true, modeDisplay: robotState.SIMSTR });
    const simulation = new Promise((resolve, reject) => {
      logging.log(`Beginning ${timings.AUTO}s ${robotState.AUTOSTR}`);
      this.props.onUpdateCodeStatus(robotState.AUTONOMOUS);
      const timestamp = Date.now();
      const autoInt = setInterval(() => {
        const diff = Math.trunc((Date.now() - timestamp) / timings.SEC);
        if (diff > timings.AUTO) {
          clearInterval(autoInt);
          resolve();
        } else if (!this.state.simulate) {
          logging.log(`${robotState.AUTOSTR} Quit`);
          clearInterval(autoInt);
          reject();
        } else {
          this.setState({ modeDisplay: `${robotState.AUTOSTR}: ${timings.AUTO - diff}` });
        }
      }, timings.SEC);
    });

    simulation.then(() =>
      new Promise((resolve, reject) => {
        logging.log(`Beginning ${timings.IDLE}s Cooldown`);
        this.props.onUpdateCodeStatus(robotState.IDLE);
        const timestamp = Date.now();
        const coolInt = setInterval(() => {
          const diff = Math.trunc((Date.now() - timestamp) / timings.SEC);
          if (diff > timings.IDLE) {
            clearInterval(coolInt);
            resolve();
          } else if (!this.state.simulate) {
            clearInterval(coolInt);
            logging.log('Cooldown Quit');
            reject();
          } else {
            this.setState({ modeDisplay: `Cooldown: ${timings.IDLE - diff}` });
          }
        }, timings.SEC);
      })).then(() => {
      new Promise((resolve, reject) => {
        logging.log(`Beginning ${timings.TELEOP}s ${robotState.TELEOPSTR}`);
        this.props.onUpdateCodeStatus(robotState.TELEOP);
        const timestamp = Date.now();
        const teleInt = setInterval(() => {
          const diff = Math.trunc((Date.now() - timestamp) / timings.SEC);
          if (diff > timings.TELEOP) {
            clearInterval(teleInt);
            resolve();
          } else if (!this.state.simulate) {
            clearInterval(teleInt);
            logging.log(`${robotState.TELEOPSTR} Quit`);
            reject();
          } else {
            this.setState({ modeDisplay: `${robotState.TELEOPSTR}: ${timings.TELEOP - diff}` });
          }
        }, timings.SEC);
      }).then(() => {
        logging.log('Simulation Finished');
        this.props.onUpdateCodeStatus(robotState.IDLE);
      }, () => {
        logging.log('Simulation Aborted');
        this.props.onUpdateCodeStatus(robotState.IDLE);
      });
    });
  }

  hasUnsavedChanges() {
    return (this.props.latestSaveCode !== this.props.editorCode);
  }

  changeTheme(theme) {
    this.props.onChangeTheme(theme);
    storage.set('editorTheme', { theme }, (err) => {
      if (err) logging.log(err);
    });
  }

  increaseFontsize() {
    this.setState({ fontsize: this.props.fontSize + 1 });
    this.props.onChangeFontsize(this.props.fontSize + 1);
    storage.set('editorFontSize', { editorFontSize: this.props.fontSize + 1 }, (err) => {
      if (err) logging.log(err);
    });
  }

  handleChangeFontsize(event) {
    this.setState({ fontsize: event.target.value });
  }

  handleSubmitFontsize(event) {
    this.changeFontsizeToFont(Number(this.state.fontsize));
    event.preventDefault();
  }

  changeFontsizeToFont(fontSize) {
    if (fontSize > 28) {
      fontSize = 28;
    }
    if (fontSize < 8) {
      fontSize = 8;
    }
    this.props.onChangeFontsize(fontSize);
    this.setState({ fontsize: fontSize });
    storage.set('editorFontSize', { editorFontSize: fontSize }, (err) => {
      if (err) logging.log(err);
    });
  }

  raiseConsole() {
    this.setState({ consoleHeight: this.state.consoleHeight + windowInfo.UNIT }, () => {
      this.onWindowResize();
    });
  }

  lowerConsole() {
    this.setState({ consoleHeight: this.state.consoleHeight - windowInfo.UNIT }, () => {
      this.onWindowResize();
    });
  }

  copyConsole() {
    clipboard.writeText(this.props.consoleData.join(''));
  }

  decreaseFontsize() {
    this.setState({ fontsize: this.props.fontSize - 1 });
    this.props.onChangeFontsize(this.props.fontSize - 1);
    storage.set('editorFontSize', { editorFontSize: this.props.fontSize - 1 }, (err) => {
      if (err) logging.log(err);
    });
  }

  render() {
    const changeMarker = this.hasUnsavedChanges() ? '*' : '';
    if (this.props.consoleUnread) {
      this.toggleConsole();
    }
    return (
      <Panel bsStyle="primary">
        <Panel.Heading>
          <Panel.Title style={{ fontSize: '14px' }}>Editing: {pathToName(this.props.filepath) ? pathToName(this.props.filepath) : '[ New File ]' } {changeMarker}</Panel.Title>
        </Panel.Heading>
        <Panel.Body>
          <Form inline onSubmit={this.handleSubmitFontsize}>
            <ButtonGroup id="file-operations-buttons">
              <DropdownButton
                title="File"
                bsSize="small"
                id="choose-theme"
              >
                <MenuItem
                  onClick={this.props.onCreateNewFile}
                >New File</MenuItem>
                <MenuItem
                  onClick={this.props.onOpenFile}
                >Open</MenuItem>
                <MenuItem
                  onClick={this.props.onSaveFile}
                >Save</MenuItem>
                <MenuItem
                  onClick={_.partial(this.props.onSaveFile, true)}
                >Save As</MenuItem>
              </DropdownButton>
              <TooltipButton
                id="upload"
                text="Upload"
                onClick={this.upload}
                glyph="upload"
                disabled={false}
              />
              <TooltipButton
                id="download"
                text="Download from Robot"
                onClick={this.props.onDownloadCode}
                glyph="download"
                disabled={!this.props.runtimeStatus || this.props.ipAddress === defaults.IPADDRESS}
              />
            </ButtonGroup>
            {' '}
            <ButtonGroup id="code-execution-buttons">
              <TooltipButton
                id="run"
                text="Run"
                onClick={this.startRobot}
                glyph="play"
                disabled={this.props.isRunningCode
                || !this.props.runtimeStatus
                || this.props.fieldControlActivity}
              />
              <TooltipButton
                id="stop"
                text="Stop"
                onClick={this.stopRobot}
                glyph="stop"
                disabled={!(this.props.isRunningCode || this.state.simulate)}
              />
              <DropdownButton
                title={this.state.modeDisplay}
                bsSize="small"
                key="dropdown"
                id="modeDropdown"
                disabled={this.state.simulate
                || this.props.fieldControlActivity
                || !this.props.runtimeStatus}
              >
                <MenuItem
                  eventKey="1"
                  active={this.state.mode === robotState.TELEOP && !this.state.simulate}
                  onClick={() => {
                    this.setState({ mode: robotState.TELEOP, modeDisplay: robotState.TELEOPSTR });
                  }}
                >
                  Tele-Operated
                </MenuItem>
                <MenuItem
                  eventKey="2"
                  active={this.state.mode === robotState.AUTONOMOUS && !this.state.simulate}
                  onClick={() => {
                    this.setState({ mode: robotState.AUTONOMOUS, modeDisplay: robotState.AUTOSTR });
                  }}
                >
                  Autonomous
                </MenuItem>
                <MenuItem
                  eventKey="3"
                  active={this.state.simulate}
                  onClick={this.simulateCompetition}
                >
                  Simulate Competition
                </MenuItem>
              </DropdownButton>
              <TooltipButton
                id="e-stop"
                text="E-STOP"
                onClick={this.estop}
                glyph="fire"
                disabled={false}
              />
            </ButtonGroup>
            {' '}
            <ButtonGroup id="console-buttons">
              <TooltipButton
                id="toggle-console"
                text="Toggle Console"
                onClick={this.toggleConsole}
                glyph="console"
                disabled={false}
                bsStyle={this.props.consoleUnread ? 'danger' : ''}
              />
              <TooltipButton
                id="clear-console"
                text="Clear Console"
                onClick={this.props.onClearConsole}
                glyph="remove"
                disabled={false}
              />
              <TooltipButton
                id="raise-console"
                text="Raise Console"
                onClick={this.raiseConsole}
                glyph="arrow-up"
                disabled={this.state.consoleHeight > windowInfo.CONSOLEMAX}
              />
              <TooltipButton
                id="lower-console"
                text="Lower Console"
                onClick={this.lowerConsole}
                glyph="arrow-down"
                disabled={this.state.consoleHeight < windowInfo.CONSOLEMIN}
              />
              <TooltipButton
                id="copy-console"
                text="Copy Console"
                onClick={this.copyConsole}
                glyph="copy"
                disabled={false}
              />
            </ButtonGroup>
            {' '}
            <FormGroup>
              <InputGroup>
                <FormControl
                  type="number"
                  value={this.state.fontsize}
                  bsSize="small"
                  onChange={this.handleChangeFontsize}
                  style={{ width: 32, padding: 6 }}
                />
                <OverlayTrigger placement="top" overlay={<Tooltip id="tooltip">Text Size</Tooltip>}>
                  <DropdownButton
                    componentClass={InputGroup.Button}
                    title=""
                    bsSize="small"
                    id="choose-font-size"
                  >
                    <MenuItem
                      class="dropdown-item"
                      onClick={() => this.changeFontsizeToFont(8)}
                    >8</MenuItem>
                    <MenuItem
                      class="dropdown-item"
                      onClick={() => this.changeFontsizeToFont(12)}
                    >12</MenuItem>
                    <MenuItem
                      class="dropdown-item"
                      onClick={() => this.changeFontsizeToFont(14)}
                    >14</MenuItem>
                    <MenuItem
                      class="dropdown-item"
                      onClick={() => this.changeFontsizeToFont(16)}
                    >16</MenuItem>
                    <MenuItem
                      class="dropdown-item"
                      onClick={() => this.changeFontsizeToFont(20)}
                    >20</MenuItem>
                    <MenuItem
                      class="dropdown-item"
                      onClick={() => this.changeFontsizeToFont(24)}
                    >24</MenuItem>
                    <MenuItem
                      class="dropdown-item"
                      onClick={() => this.changeFontsizeToFont(28)}
                    >28</MenuItem>
                  </DropdownButton>
                </OverlayTrigger>
              </InputGroup>
            </FormGroup>
            {' '}
            <ButtonGroup id="editor-settings-buttons" class="form-inline">
              <TooltipButton
                id="increase-font-size"
                text="Increase font size"
                onClick={this.increaseFontsize}
                glyph="zoom-in"
                disabled={this.props.fontSize >= 28}
              />
              <TooltipButton
                id="decrease-font-size"
                text="Decrease font size"
                onClick={this.decreaseFontsize}
                glyph="zoom-out"
                disabled={this.props.fontSize <= 8}
              />
              <DropdownButton
                title="Theme"
                bsSize="small"
                id="choose-theme"
              >
                {this.themes.map(theme => (
                  <MenuItem
                    active={theme === this.props.editorTheme}
                    onClick={_.partial(this.changeTheme, theme)}
                    key={theme}
                  >
                    {theme}
                  </MenuItem>
                ))}
              </DropdownButton>
            </ButtonGroup>
          </Form>

          <AceEditor
            mode="python"
            theme={this.props.editorTheme}
            width="100%"
            fontSize={this.props.fontSize}
            ref={(input) => { this.CodeEditor = input; }}
            name="CodeEditor"
            height={this.state.editorHeight.toString()}
            value={this.props.editorCode}
            onChange={this.props.onEditorUpdate}
            onPaste={Editor.onEditorPaste}
            editorProps={{ $blockScrolling: Infinity }}
          />
          <ConsoleOutput
            toggleConsole={this.toggleConsole}
            show={this.props.showConsole}
            height={this.state.consoleHeight}
            output={this.props.consoleData}
            disableScroll={this.props.disableScroll}
          />
        </Panel.Body>
      </Panel>
    );
  }
}

Editor.propTypes = {
  editorCode: PropTypes.string.isRequired,
  editorTheme: PropTypes.string.isRequired,
  filepath: PropTypes.string.isRequired,
  fontSize: PropTypes.number.isRequired,
  latestSaveCode: PropTypes.string.isRequired,
  showConsole: PropTypes.bool.isRequired,
  consoleData: PropTypes.array.isRequired,
  onAlertAdd: PropTypes.func.isRequired,
  onEditorUpdate: PropTypes.func.isRequired,
  onSaveFile: PropTypes.func.isRequired,
  onDragFile: PropTypes.func.isRequired,
  onOpenFile: PropTypes.func.isRequired,
  onCreateNewFile: PropTypes.func.isRequired,
  onChangeTheme: PropTypes.func.isRequired,
  onChangeFontsize: PropTypes.func.isRequired,
  toggleConsole: PropTypes.func.isRequired,
  onClearConsole: PropTypes.func.isRequired,
  onUpdateCodeStatus: PropTypes.func.isRequired,
  isRunningCode: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  ipAddress: PropTypes.string.isRequired,
  fieldControlActivity: PropTypes.bool.isRequired,
  onDownloadCode: PropTypes.func.isRequired,
  onUploadCode: PropTypes.func.isRequired,
  disableScroll: PropTypes.bool.isRequired,
  consoleUnread: PropTypes.bool.isRequired,
};

export default Editor;
