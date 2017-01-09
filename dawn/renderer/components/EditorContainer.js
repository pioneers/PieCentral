import { connect } from 'react-redux';
import Editor from './Editor';
import {
  editorUpdate,
  saveFile,
  openFile,
  createNewFile,
} from '../actions/EditorActions.js';
import {
  changeTheme,
  changeFontsize,
} from '../actions/SettingsActions.js';
import {
  showConsole,
  hideConsole,
  clearConsole,
} from '../actions/ConsoleActions';
import { addAsyncAlert } from '../actions/AlertActions';

const mapStateToProps = (state) => ({
  editorCode: state.editor.editorCode,
  editorTheme: state.settings.editorTheme,
  filepath: state.editor.filepath,
  fontSize: state.settings.fontSize,
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
});

const EditorContainer = connect(mapStateToProps, mapDispatchToProps)(Editor);

export default EditorContainer;
