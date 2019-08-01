import io from 'socket.io-client';
import store from './store';
import { updateTimer } from './game/match';

// FIXME
export const socket = io(`http://127.0.0.1:8100`);

socket.on('timer', update => store.dispatch(updateTimer(update)));
// socket.on('match')
