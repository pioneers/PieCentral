import { StatusType } from '../constants/Constants';

const DEFAULT_CONNECTION = {
  status: StatusType.DISCONNECTED,
};

const connection = (state = DEFAULT_CONNECTION, action) => {
  switch (action.type) {
    default:
      return state;
  }
};

export default connection;
