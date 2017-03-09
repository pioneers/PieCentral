export const infoPerMessage = stateChange => ({
  type: 'PER_MESSAGE',
  robotState: stateChange,
});

export const ansibleDisconnect = () => ({
  type: 'ANSIBLE_DISCONNECT',
});

export const runtimeConnect = () => ({
  type: 'RUNTIME_CONNECT',
});

export const runtimeDisconnect = () => ({
  type: 'RUNTIME_DISCONNECT',
});

export const updateBattery = battery => ({
  type: 'UPDATE_BATTERY',
  battery,
});

export const updateCodeStatus = studentCodeStatus => ({
  type: 'CODE_STATUS',
  studentCodeStatus,
});

export const ipChange = ipAddress => ({
  type: 'IP_CHANGE',
  ipAddress,
});

export const notifyChange = hold => ({
  type: 'NOTIFICATION_CHANGE',
  notificationHold: hold,
});
