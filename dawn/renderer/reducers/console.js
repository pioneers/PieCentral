const DEFAULT_CONSOLE = {
  lines: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'],
  isOpen: true,
};

const console = (state = DEFAULT_CONSOLE, action) => {
  switch (action.type) {
    case 'OPEN':
    case 'CLOSE':
      return {...state, isOpen: action.payload.isOpen};
    // case 'APPEND':
    //   return {...state, lines: };
    case 'CLEAR':
      return {...state, lines: []};
    default:
      return state;
  }
};

export default console;
