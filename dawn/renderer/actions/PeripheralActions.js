export const updatePeripherals = sensors => ({
  type: 'UPDATE_PERIPHERALS',
  peripherals: sensors,
});

export const peripheralRename = (uid, newname) => ({
  type: 'PERIPHERAL_RENAME',
  id: uid,
  name: newname,
});
