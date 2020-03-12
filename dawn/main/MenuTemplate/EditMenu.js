/*
 * Defines the edit menu.
 */

const EditMenu = {
  label: 'Edit',
  submenu: [
    {
      label: 'Cut',
      accelerator: 'CommandOrControl+X',
      role: 'cut',
    },
    {
      label: 'Copy',
      accelerator: 'CommandOrControl+C',
      role: 'copy',
    },
    {
      label: 'Paste',
      accelerator: 'CommandOrControl+V',
      role: 'paste',
    },
  ],
};

export default EditMenu;
