'use strict'

angular.module('daemon.radio', [])

.service('radio', [
  '$interval'
  ($interval) ->
    # whether or not we've initialized
    _init = false
    # an object of arrays, where the keys are
    # the channel of events to repond to
    # and the values are arrays of callbacks
    callbacks = {}

    # send an update to each callback that has registered with us
    # but only if the radio is initialized
    processUpdate = (channel, update) ->
      if _init and callbacks[channel]?
        callback(channel, update) for callback in callbacks[channel]

    # fake radio event sent every 100 ms
    mockEnabled = false
    mockPromise = undefined
    mockRadio = ->
      now = new Date().getTime()
      num = Math.random()
      processUpdate('mock', {
        id: '1234567890'
        time: now
        value: num
        })

    SerialPort = require("serialport").SerialPort
    radioAddr = "AAAAAAAAAAAAAAAA"
    serialPort = new SerialPort("/dev/ttyUSB0",
      baudrate: 57600
    )

    radio = require('kyleradio')
    rad = new radio.Radio()

    rad.connectXBee(radioAddr, serialPort)
    $interval( ->
      console.log 'try to send shit'
      rad.send({'PiELESAnalogValues': [127,127,127,127,127,127,127]})
    , 100)
    
    return {
      init: ->
        _init = true
        return true
      enableMock: (millis = 100) ->
        unless mockEnabled
          mockEnabled = true
          mockPromise = $interval(mockRadio, millis)
      initialized: ->
        return _init
      close: ->
        _init = false
        $interval.cancel(mockPromise)
        mockEnabled = false
        callbacks = {}
        return true
      onReceive: (channels..., callback) ->
        return false unless _init # exit if we're not initialized

        for channel in channels
          callbacks[channel] = [] unless callbacks[channel]?
          callbacks[channel].push callback
        return true
      send: (channels..., object) ->
        return false unless _init # exit if we're not initialized

        for channel in channels
          console.log "radio channel 'chname': fake sent object"
          .replace(/object/, String(object))
          .replace(/chname/, channel)
        return true
    }
])