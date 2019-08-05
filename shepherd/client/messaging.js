import io from 'socket.io-client';
import store from './store';
import { updateTimer } from './game/match';
import { updateResources } from './game/resource';

export const SERVER_HOST = SERVER_HOST || '127.0.0.1';
export const SERVER_PORT = SERVER_PORT || 8100;

export const socket = io(`http://${SERVER_HOST}:${SERVER_PORT}`);

socket.on('timer', update => store.dispatch(updateTimer(update)));
socket.on('resources', update => store.dispatch(updateResources(update)));
