import io from 'socket.io-client';
import store from './store';
import { updateTimer } from './game/match';

export const socket = io(`http://localhost:8100`);

socket.on('timer', update => store.dispatch(updateTimer(update)));
