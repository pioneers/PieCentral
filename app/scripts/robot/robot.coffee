'use strict'

angular.module('daemon.robot', ['daemon.peripheral', 'daemon.gamepad'])

.service('robot', [
  '$interval'
  'gamepads'
  'Peripheral'
  'Gamepad'

  ($interval, radio, gamepads, Peripheral, Gamepad) ->
    _peripherals = []
    _peripherals.push(new Peripheral(-1, 'Mock Peripheral'))

    for g in gamepads.active()
      gpad = new Gamepad(g, g.id, 'Gamepad ' + g.index)
      _peripherals.push(gpad)
      gamepads.onUpdate(gpad.update)

    findPeripheral = (properties) ->
      switch typeof properties
        when 'number' then _.findWhere(_peripherals, id: properties)
        else # assume object
          _.findWhere(_peripherals, properties)

    return {
      peripherals: ->
        return _peripherals
      peripheral: findPeripheral
    }
  ])
