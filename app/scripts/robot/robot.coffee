'use strict'

angular.module('daemon.robot', ['daemon.radio', 'daemon.peripheral', 'daemon.gamepad'])

.service('robot', [
  '$interval'
  'radio'
  'gamepads'
  'Peripheral'
  'Gamepad'

  ($interval, radio, gamepads, Peripheral, Gamepad) ->
    _lastContact = Date.now()
    _peripherals = []
    _peripherals.push(new Peripheral(-1, 'Mock Peripheral'))

    for g in gamepads.active()
      gpad = new Gamepad(g, g.id, 'Gamepad ' + g.index)
      _peripherals.push(gpad)
      gamepads.onUpdate(gpad.update)

    updateLastContact = ->
      _lastContact = Date.now()

    findPeripheral = (properties) ->
      switch typeof properties
        when 'number' then _.findWhere(_peripherals, id: properties)
        else # assume object
          _.findWhere(_peripherals, properties)


    radio.enableMock()
    radio.onReceive('mock', (channel, update) ->
      updateLastContact()
      findPeripheral(-1).update channel, update
    )

    return {
      lastContact: ->
        return _lastContact
      peripherals: ->
        return _peripherals
      peripheral: findPeripheral
    }
  ])
