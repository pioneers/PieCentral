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

export const masterStatus = () => ({
  type: 'MASTER_ROBOT',
});

export const runtimeDisconnect = () => ({
  type: 'RUNTIME_DISCONNECT',
});

export const updateCodeStatus = studentCodeStatus => ({
  type: 'CODE_STATUS',
  studentCodeStatus,
});

export const ipChange = ipAddress => ({
  type: 'IP_CHANGE',
  ipAddress,
});
