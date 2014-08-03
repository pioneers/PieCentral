'use strict'

angular.module('daemon.robot', ['daemon.radio'])

.service('robot', [
  'radio'
  'Peripheral'
  (radio, Peripheral) ->
    _lastContact = Date.now()
    _peripherals = []
    _peripherals.push(new Peripheral(-1, 'Mock Peripheral'))

    updateLastContact = ->
      _lastContact = Date.now()

    findPeripheral = (properties) ->
      switch typeof properties
        when 'number' then _.findWhere(_peripherals, id: properties)
        else # assume object
          _.findWhere(_peripherals, properties)


    radio.init()
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