import { connect } from 'react-redux';
import Editor from './Editor';
import {
  editorUpdate,
} from '../actions/EditorActions.js';
import {
  changeTheme,
  increaseFontsize,
  decreaseFontsize,
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

const EditorContainer = connect(mapStateToProps, mapDispatchToProps)(Editor);

export default EditorContainer;
