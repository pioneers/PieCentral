import { expect } from 'chai';
import { toggleConsole, updateConsole, clearConsole } from '../ConsoleActions';


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
  it('should create an action to toggle console', () => {
    const expectedAction = {
      type: 'TOGGLE_CONSOLE',
    };
    expect(toggleConsole()).to.deep.equal(expectedAction);
  });
});
