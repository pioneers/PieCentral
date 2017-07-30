import { connect } from 'react-redux';
import Editor from './Editor';
import {
  editorUpdate,
  saveFile,
  openFile,
  createNewFile,
  downloadCode,
} from '../actions/EditorActions';
import {
  changeTheme,
  changeFontsize,
} from '../actions/SettingsActions';
import {
  toggleConsole,
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
  notificationHold: state.info.notificationHold,
  fieldControlActivity: state.info.fieldControlActivity,
  disableScroll: state.studentConsole.disableScroll,
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
  toggleConsole: () => {
    dispatch(toggleConsole());
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
  onDownloadCode: () => {
    dispatch(downloadCode());
  },
});

const EditorContainer = connect(mapStateToProps, mapDispatchToProps)(Editor);

export default EditorContainer;
