export const updatePeripherals = sensors => ({
  type: 'UPDATE_PERIPHERALS',
  peripherals: sensors,
});

export const peripheralDisconnect = uid => ({
  type: 'PERIPHERAL_DISCONNECT',
  id: uid,
});

export const peripheralRename = (uid, newname) => ({
  type: 'PERIPHERAL_RENAME',
  id: uid,
  name: newname,
});
