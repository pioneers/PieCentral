import { expect } from 'chai';
import { showConsole, hideConsole } from '../ConsoleActions';

describe('console action creator', () => {
  it('create showConsole action', () => {
    expect(showConsole()).to.deep.equal({
      type: 'SHOW_CONSOLE',
    });
  });
});
