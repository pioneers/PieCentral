import { expect } from 'chai';
import asyncAlerts from '../alerts';

describe('alerts reducer', () => {
  it('should return default state', () => {
    const action = { type: 'NOT_A_TYPE' };
    const initialState = [];
    expect(asyncAlerts(initialState, action)).to.equal(initialState);
  });

  it('should handle adding an alert', () => {
    const action = {
      heading: 'example alert',
      id: 1,
      message: 'example message',
      type: 'ADD_ASYNC_ALERT',
    };
    expect(asyncAlerts([], action)).to.deep.equal([
      {
        heading: 'example alert',
        id: 1,
        message: 'example message',
      },
    ]);
  });

  it('should handle having multiple alerts', () => {
    const initialState = [
      {
        heading: 'first alert',
        id: 1,
        message: 'first message',
      },
    ];
    const action = {
      heading: 'second alert',
      id: 2,
      message: 'second message',
      type: 'ADD_ASYNC_ALERT',
    };
    expect(asyncAlerts(initialState, action)).to.deep.equal([
      {
        heading: 'first alert',
        id: 1,
        message: 'first message',
      },
      {
        heading: 'second alert',
        id: 2,
        message: 'second message',
      },
    ]);
  });

  it('should handle removing of alerts', () => {
    const initialState = [
      {
        heading: 'first alert',
        id: 1,
        message: 'first message',
      },
      {
        heading: 'second alert',
        id: 2,
        message: 'second message',
      },
    ];
    const action = {
      id: 1,
      type: 'REMOVE_ASYNC_ALERT',
    };
    expect(asyncAlerts(initialState, action)).to.deep.equal([
      {
        heading: 'second alert',
        id: 2,
        message: 'second message',
      },
    ]);
  });
});
