export const pathToName = (filepath) => {
  if (filepath !== null) {
    if (process.platform === 'win32') {
      return filepath.split('\\').pop();
    }
    return filepath.split('/').pop();
  }
  return false;
};

export const getValidationState = (testIPAddress) => {
  let valid = false;
  const regex = '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}' +
    '((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))$';
  if ((new RegExp(regex, 'g')).test(testIPAddress)) {
    valid = true;
  }
  if (valid) {
    return 'success';
  } else if (testIPAddress === 'localhost') {
    return 'warning';
  }
  return 'error';
};

export const uploadStatus = {
  RECEIVED: 0,
  SENT: 1,
  ERROR: 2,
};

export const stateEnum = {
  IDLE: 0,
  TELEOP: 1,
  AUTONOMOUS: 2,
  ESTOP: 3,
};
