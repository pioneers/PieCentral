import { expect } from 'chai';
import { changeTheme, increaseFontsize, decreaseFontsize } from '../SettingsActions.js';

describe('settings actions creator', () => {
  it('should create an action to change theme', () => {
    const expectedAction = {
      type: 'CHANGE_THEME',
      theme: 'monokai',
    };
    expect(changeTheme('monokai')).to.deep.equal(expectedAction);
  });
  it('should create an action to increase font size', () => {
    const expectedAction = {
      type: 'INCREASE_FONTSIZE',
    };
    expect(increaseFontsize()).to.deep.equal(expectedAction);
  });
  it('should create an action to decrease font size', () => {
    const expectedAction = {
      type: 'DECREASE_FONTSIZE',
    };
    expect(decreaseFontsize()).to.deep.equal(expectedAction);
  });
});
