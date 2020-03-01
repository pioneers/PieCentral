import { ConnectionStatus } from '../constants/Constants';

const DEFAULT_CONNECTION = {
  status: ConnectionStatus.DISCONNECTED,
  heartbeats: [],
};

const MAX_HEARTBEATS = 50;

const connection = (state = DEFAULT_CONNECTION, action) => {
  switch (action.type) {
    case 'ADD_HEARTBEAT':
      let index = state.heartbeats.length - MAX_HEARTBEATS;
      return {
        ...state,
        heartbeats: [...state.heartbeats, action.payload].slice(index),
      };
    case 'SET_STATUS':
      return { ...state, status: action.payload.status };
    default:
      return state;
  }
};

export default connection;
