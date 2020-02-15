const DEFAULT_CONSOLE = {
  records: [{'event': 'Starting'}],
  isOpen: true,
};

const console = (state = DEFAULT_CONSOLE, action) => {
  switch (action.type) {
    case 'TOGGLE':
      return {...state, isOpen: !state.isOpen};
    case 'APPEND':
      return {...state, records: [...state.records, action.payload]};
    case 'CLEAR':
      return {...state, records: []};
    default:
      return state;
  }
};

export default console;
