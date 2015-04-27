describe 'ansible/reporters', ->

  gamepadReporter = undefined
  $interval = undefined
  ansible = undefined
  beforeEach ->
    module 'ansible'
    inject (_gamepadReporter_, _$interval_, _ansible_) ->
      gamepadReporter = _gamepadReporter_
      $interval = _$interval_
      ansible = _ansible_

  describe 'gamepadReporter, when gamepad connected', ->
    beforeEach ->
      spyOn(navigator, 'getGamepads').and.returnValue([
          axes: [0, 1, 0, 1]
          buttons: [{value: 0} for i in [0..17]]
        ])
      spyOn(ansible, 'send')
      $interval.flush(100)

    it 'calls navigator.getGamepads', ->
      expect(navigator.getGamepads).toHaveBeenCalled()

    it 'calls ansible.send', ->
      expect(ansible.send).toHaveBeenCalled()
