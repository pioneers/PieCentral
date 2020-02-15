const DEFAULT_CONSOLE = {
  lines: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'],
  isOpen: true,
};

const console = (state = DEFAULT_CONSOLE, action) => {
  switch (action.type) {
    case 'TOGGLE':
      return {...state, isOpen: !state.isOpen};
    case 'APPEND':
      return {...state, lines: [...state.lines, ...action.payload.lines]};
    case 'CLEAR':
      return {...state, lines: []};
    default:
      return state;
  }
};

export default console;
