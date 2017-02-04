export const ansibleConnect = () => ({
  type: 'ANSIBLE_CONNECT',
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

export const updateRobotState = robotState => ({
  type: 'ROBOT_STATE',
  robotState,
});

export const updateStatus = () => ({
  type: 'UPDATE_STATUS',
});

export const ipChange = ipAddress => ({
  type: 'IP_CHANGE',
  ipAddress,
});
