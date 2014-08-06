angular.module('daemon.peripheral', ['daemon.gamepad'])

.factory('Peripheral', [
  ->
    (id, name = 'default', memoryLength = 10) ->
      _updateHistory = [{time: Date.now(), value: 0}]

      # removes elements of history older than memoryLength seconds ago
      # not very expensive
      cleanHistory = ->
        cutoff = _.sortedIndex(_updateHistory,
          {time: Date.now() - 1000 * memoryLength}, 'time')
        _updateHistory.splice 0, cutoff

      ###
      Publicly accessible methods
      ###

      historyPairs = () ->
        return _updateHistory

      # update the Peripheral
      update = (channel, update) ->
        # insert the update in sorted order
        insertIndex = _.sortedIndex(_updateHistory, update, 'time')
        _updateHistory.splice insertIndex, 0, update
        cleanHistory()

      return {
        id: id
        name: name
        historyPairs: historyPairs
        update: update
        lastUpdate: -> _.last(_updateHistory)
      }
  ])

.factory('Gamepad', [
  'Peripheral'

  (Peripheral) ->
    (gamepad, id, name = 'default', memoryLength = 10) ->
      _gamepad = gamepad
      _actions = []

      buttonNames = [
        'aButton'
        'bButton'
        'xButton'
        'yButton'
        'leftBumper'
        'rightBumper'
        'leftTrigger'
        'rightTrigger'
        'backButton'
        'startButton'
        'leftStickIn'
        'rightStickIn'
        'upDpad'
        'downDpad'
        'leftDpad'
        'rightDpad'
        'xboxButton'
      ]

      genID = (buttonIndex) ->
        (_gamepad.index * 8) + buttonIndex

      for i in [0..8] by 1
        _actions.push({
          periph: new Peripheral(genID(i), buttonNames[i], memoryLength)
          index: i
          })

      update = ->
        for action in _actions
          action.periph.update(action.periph.name, {time: Date.now(), value: _gamepad.buttons[action.index]})

      subPeripherals = ->
        subPeriphs = []
        for action in _actions
          subPeriphs.push(action.periph)
        return subPeriphs

      return {
        id: id
        name: name
        update: -> update()
        subPeripherals: -> subPeripherals()
      }
  ])