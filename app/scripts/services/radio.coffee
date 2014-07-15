'use strict'

angular.module('daemon.radio', [])

.service('radio', [
  '$interval'
  ($interval) ->
    # whether or not we've initialized
    _init = false
    # an object of arrays, where the keys are
    # the type of events to repond to
    # and the values are arrays of callbacks
    callbacks = {}

    # send an update to each callback that has registered with us
    # but only if the radio is initialized
    processUpdate = (update) ->
      if _init and callbacks[update.type]?
        callback(update) for callback in callbacks[update.type]

    # fake radio event sent every 100 ms
    mockEnabled = false
    mockRadio = ->
      now = new Date().getTime()
      num = Math.random()
      processUpdate({
        type: 'mock'
        id: '1234567890'
        time: now
        value: num
        })
    return {
      init: ->
        _init = true
        return true
      enableMock: (millis = 100) ->
        unless mockEnabled
          mockEnabled = true
          $interval(mockRadio, millis)
      initialized: ->
        return _init
      close: ->
        _init = false
        callbacks = {}
        return true
      onReceive: (type, callback) ->
        if _init
          callbacks[type] = [] unless callbacks[type]?
          callbacks[type].push callback
          return true
        else
          return false
    }
])