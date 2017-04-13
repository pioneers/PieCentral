import AppDispatcher from '../dispatcher/AppDispatcher';
import { EventEmitter } from 'events';
import assign from 'object-assign';
import { ActionTypes } from '../constants/Constants';
import _ from 'lodash';

let _alerts = [];
let AlertStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getLatestAlert() {
    return _alerts[0];
  }
});

let addAlert = function(alert) {
  if (_.some(_alerts, _.matches(alert))) {
    return;
  } else {
    _alerts.push(alert);
  }
  AlertStore.emitChange();
};

let removeAlert = function(alert) {
  _.remove(_alerts, _.matches(alert));
  AlertStore.emitChange();
};

AlertStore.dispatchToken = AppDispatcher.register((action)=>{
  switch (action.type) {
    case ActionTypes.ADD_ALERT:
      addAlert(action.payload);
      break;
    case ActionTypes.REMOVE_ALERT:
      removeAlert(action.payload);
      break;
  }
});

export default AlertStore;
