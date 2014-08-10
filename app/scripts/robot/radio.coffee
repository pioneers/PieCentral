'use strict'

angular.module('daemon.radio', [])

.service('radio', [
  '$interval'
  ($interval) ->
    # whether or not we've initialized
    _init = false

    # thing
    _ndl3Radio = undefined

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

    radioInit = (radioAddr = "0013A20040A580C4", portPath = "/dev/ttyUSB0") ->
      SerialPort = requireNode("serialport").SerialPort
      serialPort = new SerialPort(portPath, baudrate: 57600, false)

      radio = requireNode('kyleradio')
      _ndl3Radio = new radio.Radio()

      serialPort.open( (error) ->
        if error
          console.log('failed to open: ' + error)
        _ndl3Radio.connectXBee(radioAddr, serialPort)
        _ndl3Radio.on('string', (str) ->
          console.log('got string', str)
          )
        )

    return {
      init: ->
        unless _init
          radioInit()
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
        return false unless object?

        for channel in channels

          if _ndl3Radio
            if channel == 'robotCode'
              _ndl3Radio.send(object, 'code')
            else
              object._channel = channel
              _ndl3Radio.send(object)
          else
            console.log "_ndl3Radio not defined"
            return false

          console.log "radio channel 'chname': sent \nobject"
          .replace(/object/, JSON.stringify(object, null, 4))
          .replace(/chname/, channel)
        return true
    }
])
