import { eventChannel } from 'redux-saga';
import { ipcRenderer } from 'electron';
import { all, delay, fork, takeLatest } from 'redux-saga/effects';

function *sendDatagrams(period = 50) {
  while (true) {
    ipcRenderer.send('sendDatagram', {}, '127.0.0.1');  // FIXME
    yield delay(period);
  }
}

export default function *effects() {
  yield all([
    fork(sendDatagrams),
    // takeLatest('CONNECT', connect),
  ]);
}
