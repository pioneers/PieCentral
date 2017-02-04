import { connect } from 'react-redux';
import Editor from './Editor';
import {
  editorUpdate,
  saveFile,
  openFile,
  createNewFile,
} from '../actions/EditorActions';
import {
  changeTheme,
  changeFontsize,
} from '../actions/SettingsActions';
import {
  showConsole,
  hideConsole,
  clearConsole,
} from '../actions/ConsoleActions';
import { addAsyncAlert } from '../actions/AlertActions';
import { updateCodeStatus, ipChange } from '../actions/InfoActions';

const mapStateToProps = state => ({
  editorCode: state.editor.editorCode,
  editorTheme: state.settings.editorTheme,
  filepath: state.editor.filepath,
  fontSize: state.settings.fontSize,
  latestSaveCode: state.editor.latestSaveCode,
  showConsole: state.studentConsole.showConsole,
  consoleData: state.studentConsole.consoleData,
  ipAddress: state.info.ipAddress,
  connectionStatus: state.info.connectionStatus,
  port: state.info.port,
  username: state.info.username,
  password: state.info.password,
});

const mapDispatchToProps = dispatch => ({
  onAlertAdd: (heading, message) => {
    dispatch(addAsyncAlert(heading, message));
  },
  onEditorUpdate: (newVal) => {
    dispatch(editorUpdate(newVal));
  },
  onSaveFile: (saveAs) => {
    dispatch(saveFile(saveAs));
  },
  onOpenFile: () => {
    dispatch(openFile());
  },
  onCreateNewFile: () => {
    dispatch(createNewFile());
  },
  onChangeTheme: (theme) => {
    dispatch(changeTheme(theme));
  },
  onChangeFontsize: (newFontsize) => {
    dispatch(changeFontsize(newFontsize));
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
  onUpdateCodeStatus: (status) => {
    dispatch(updateCodeStatus(status));
  },
  onIPChange: (ipAddress) => {
    dispatch(ipChange(ipAddress));
  },
});

const EditorContainer = connect(mapStateToProps, mapDispatchToProps)(Editor);

export default EditorContainer;
