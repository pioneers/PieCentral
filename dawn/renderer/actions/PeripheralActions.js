export const updatePeripheral = (sensor) => ({
  type: 'UPDATE_PERIPHERAL',
  peripheral: sensor,
});

export const peripheralDisconnect = (uid) => ({
  type: 'PERIPHERAL_DISCONNECT',
  id: uid,
});
