import { eventChannel } from 'redux-saga';
import { all, fork } from 'redux-saga/effects';

export default function *effects() {
  yield all([
    // fork(),
  ]);
}
