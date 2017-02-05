import { expect } from 'chai';
import {
  openFile,
  saveFile,
  deleteFile,
  createNewFile,
  editorUpdate,
} from '../EditorActions';


describe('editor actions creator', () => {
  it('should create an action to open file', () => {
    const expectedAction = {
      type: 'OPEN_FILE',
    };
    expect(openFile()).to.deep.equal(expectedAction);
  });
  it('should create an action to save file', () => {
    const expectedAction = {
      type: 'SAVE_FILE',
      saveAs: false,
    };
    expect(saveFile()).to.deep.equal(expectedAction);
  });
  it('should create an action to save file as', () => {
    const expectedAction = {
      type: 'SAVE_FILE',
      saveAs: true,
    };
    expect(saveFile(true)).to.deep.equal(expectedAction);
  });
  it('should create an action to delete file', () => {
    const expectedAction = {
      type: 'DELETE_FILE',
    };
    expect(deleteFile()).to.deep.equal(expectedAction);
  });
  it('should create an action to create new file', () => {
    const expectedAction = {
      type: 'CREATE_NEW_FILE',
    };
    expect(createNewFile()).to.deep.equal(expectedAction);
  });
  it('should create an action to update editor', () => {
    const expectedAction = {
      type: 'UPDATE_EDITOR',
      code: 'print(x)',
    };
    expect(editorUpdate('print(x)')).to.deep.equal(expectedAction);
  });
});
