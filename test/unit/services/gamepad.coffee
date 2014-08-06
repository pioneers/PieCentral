describe 'daemon.gamepad', ->
  gamepad = undefined
  beforeEach ->
    module 'daemon.gamepad'
    inject (_gamepad_) -> gamepad = _gamepad_