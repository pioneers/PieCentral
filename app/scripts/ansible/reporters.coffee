angular.module('ansible')

# reports the gamepad states
.service 'gamepadReporter', [
  '$interval'
  'ansible'
  'AMessage'
  ($interval, ansible, AMessage) ->

    # used for not sending redundant gamepad state
    previousTimestamp = 0
    update = ->
      g = navigator.getGamepads()[0]
      if not g? or g.timestamp == previousTimestamp
        return # we don't have anything to send

      previousTimestamp = g.timestamp

      content =
        axes: g.axes
        buttons: _.map(g.buttons, (b) -> b.value)

      message = new AMessage('gamepad', content)
      ansible.send(message)

    $interval(update, 20) # fastest practical for gamepad api
  ]
