import keyMirror from 'keymirror';

module.exports = {
  VERSION: '0.4.0',
  ActionTypes: keyMirror({
    RECEIVE_ANSIBLE_MESSAGE: null,
    UPDATE_GAMEPADS: null,
    UPLOAD_CODE: null
  })
};
