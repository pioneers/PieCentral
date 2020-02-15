const DEFAULT_CONSOLE = {
  records: [{'event': 'Starting'}],
  isOpen: true,
  maxLines: 256,
};

const console = (state = DEFAULT_CONSOLE, action) => {
  let records;
  switch (action.type) {
    case 'TOGGLE':
      return {...state, isOpen: !state.isOpen};
    case 'CLEAR':
      return {...state, records: []};
    case 'APPEND':
      records = state.records.slice(-(state.maxLines - 1));
      records.push(action.payload.record);
      return {...state, records};
    case 'TRUNCATE':
      let { maxLines } = action.payload;
      records = state.records.slice(-maxLines);
      return {...state, maxLines: maxLines, records};
    default:
      return state;
  }
};

export default console;
