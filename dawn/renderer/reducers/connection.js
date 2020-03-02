import { ConnectionStatus } from '../constants/Constants';

const DEFAULT_CONNECTION = {
  status: ConnectionStatus.DISCONNECTED,
  heartbeats: [],
  match: {
    mode: null,  // TODO: initialize
    alliance: null,
  },
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
    case 'SET_MATCH':
      return { ...state, match: { ...state.match, ...action.payload } };
    case 'SET_CONNECTION_STATUS':
      let { status } = action.payload;
      let heartbeats = status === ConnectionStatus.DISCONNECTED ? [] : state.heartbeats;
      return { ...state, status, heartbeats };
    default:
      return state;
  }
};

export default connection;
