angular.module('ansible')

# reports the gamepad states
.service 'gamepadReporter', [
  '$interval'
  'ansible'
  'AMessage'
  ($interval, ansible, AMessage) ->
    update = ->
      g = navigator.getGamepads()[0]
      if not g?
        return # we don't have anything to send

      content =
        axes: g.axes
        buttons: _.map(g.buttons, (b) -> b.value)

      message = new AMessage('gamepad', content)
      ansible.send(message)

    $interval(update, 100)
  ]
