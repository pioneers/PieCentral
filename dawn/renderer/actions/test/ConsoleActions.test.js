import { expect } from 'chai';
import { showConsole, hideConsole, updateConsole, clearConsole } from '../ConsoleActions';


describe('console actions creator', () => {
  it('should create an action to update console', () => {
    const expectedAction = {
      type: 'UPDATE_CONSOLE',
      consoleOutput: 'Hello World',
    };
    expect(updateConsole('Hello World')).to.deep.equal(expectedAction);
  });
  it('should create an action to clear console', () => {
    const expectedAction = {
      type: 'CLEAR_CONSOLE',
    };
    expect(clearConsole()).to.deep.equal(expectedAction);
  });
  it('should create an action to show console', () => {
    const expectedAction = {
      type: 'SHOW_CONSOLE',
    };
    expect(showConsole()).to.deep.equal(expectedAction);
  });
  it('should create an action to hide console', () => {
    const expectedAction = {
      type: 'HIDE_CONSOLE',
    };
    expect(hideConsole()).to.deep.equal(expectedAction);
  });
});
