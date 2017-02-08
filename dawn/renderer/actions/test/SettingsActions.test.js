import { expect } from 'chai';
import { changeTheme, changeFontsize } from '../SettingsActions';

describe('settings actions creator', () => {
  it('should create an action to change theme', () => {
    const expectedAction = {
      type: 'CHANGE_THEME',
      theme: 'monokai',
    };
    expect(changeTheme('monokai')).to.deep.equal(expectedAction);
  });
  it('should create an action to change font size', () => {
    const expectedAction = {
      type: 'CHANGE_FONTSIZE',
      newFontsize: 16,
    };
    expect(changeFontsize(16)).to.deep.equal(expectedAction);
  });
});
