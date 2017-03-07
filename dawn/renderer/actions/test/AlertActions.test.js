import seedrandom from 'seedrandom';
import { expect } from 'chai';
import { addAsyncAlert, removeAsyncAlert } from '../AlertActions';


describe('alerts action creator', () => {
  // Needs to be using the same seed as the action creator.
  const rng = seedrandom('alertseed');

  it('should create an action to add alert', () => {
    const expectedAction = {
      type: 'ADD_ASYNC_ALERT',
      id: rng.int32(),
      heading: 'example alert',
      message: 'example message',
    };
    expect(addAsyncAlert(
      'example alert', 'example message',
    )).to.deep.equal(expectedAction);
  });

  it('should create an action remove an alert', () => {
    const expectedAction = {
      type: 'REMOVE_ASYNC_ALERT',
      id: 0,
    };
    expect(removeAsyncAlert(0)).to.deep.equal(expectedAction);
  });
});
