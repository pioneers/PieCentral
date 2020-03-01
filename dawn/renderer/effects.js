import { eventChannel } from 'redux-saga';
import { ipcRenderer } from 'electron';
import { all, delay, fork, put, takeLatest, select } from 'redux-saga/effects';
import { addHeartbeat, setStatus } from './actions/connection';
import { ConnectionStatus } from './constants/Constants';

function *sendDatagrams(interval = 50) {
  while (true) {
    ipcRenderer.send('sendDatagram', {}, '127.0.0.1');  // FIXME
    yield delay(interval);
  }
}

const LATENCY_THRESHOLD = {
  WARNING: 200,
  DISCONNECTED: 1000,
};

function *monitorHealth(points = 5, interval = 200) {
  while (true) {
    let heartbeats = yield select((state) => state.connection.heartbeats);
    if (heartbeats.length > 0) {
      let meanInterval = (new Date() - heartbeats[0]) / heartbeats.length;  // in ms
      if (meanInterval < LATENCY_THRESHOLD.WARNING) {
        yield put(setStatus(ConnectionStatus.HEALTHY));
      } else if (meanInterval < LATENCY_THRESHOLD.DISCONNECTED) {
        yield put(setStatus(ConnectionStatus.WARNING));
      } else {
        yield put(setStatus(ConnectionStatus.DISCONNECTED));
      }
    }
    yield delay(interval);
  }
}

export default function *effects() {
  yield all([
    fork(sendDatagrams),
    fork(monitorHealth),
    // takeLatest('CONNECT', connect),
  ]);
}
