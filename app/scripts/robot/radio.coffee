'use strict'

angular.module('daemon.radio', [])

.service('radio', [
  '$interval'
  'robotConsole'
  ($interval, robotConsole) ->
    radio = {}
    # whether or not we've initialized
    _init = false

    radio.initialized = ->
      return _init

    # thing
    _ndl3Radio = undefined

    # initialize typpo

    RADIO_PROTOCOL_YAML_FILE = "./radio_protocol_ng.yaml"
    typpo_module = requireNode('ndl3radio/factory')

    typpo = typpo_module.make()
    typpo.set_target_type('ARM')
    typpo.load_type_file(RADIO_PROTOCOL_YAML_FILE, false)

    # an object of arrays, where the keys are
    # the channel of events to repond to
    # and the values are arrays of callbacks
    callbacks = {}

    # send an update to each callback that has registered with us
    # but only if the radio is initialized
    processUpdate = (channel, update) ->
      if _init and callbacks[channel]?
        callback(channel, update) for callback in callbacks[channel]

    ### MOCK RADIO STUFF
    Sends a false mock event on channel 'mock' every 100 ms
    ###
    mock = false
    mockPromise = undefined
    mockRadio = ->
      processUpdate('mock', {id: '123', time: _.now(), value: Math.random()})
    setupMock = (millis = 100) ->
      unless mock
        mock = true
        mockPromise = $interval(mockRadio, millis)

    _radioAddr = ''
    _portPath = ''
    _serialPort = undefined

    radio.init = (radioAddr, portPath) ->
      _init = true
      _radioAddr = radioAddr

      setupMock()
      _ndl3Radio.close() if _ndl3Radio?
      if requireNode?
        ndl3 = requireNode('ndl3radio')
      else
        return

      _ndl3Radio = new ndl3.Radio()
      this._ndl3Radio = _ndl3Radio

      if _portPath != portPath
        _portPath = portPath
        if _serialPort? # we have an old _serialPort to close
          _serialPort.close( (error) -> initSerialPort() )
        else # we have no _serialPort
          initSerialPort()
      else # portPath hasn't changed, and we have a _serialPort
        registerRadio()

    # make a new _serialPort and register the radio
    initSerialPort = ->
      SerialPort = requireNode("serialport").SerialPort
      _serialPort = new SerialPort(_portPath, baudrate: 57600, false)
      _serialPort.open(registerRadio)

    # register the radio with the serialport
    registerRadio = (error) ->
      if error
        console.log('failed to open: ' + error)

      _ndl3Radio.connectXBee(_radioAddr, _serialPort)
      _ndl3Radio.on('string', (str) -> robotConsole._write(str))

    radio.close = ->
      if _init
        _ndl3Radio.close() if _ndl3Radio?
        _serialPort.close() if _serialPort?
        _ndl3Radio = undefined
        _serialPort = undefined
      _init = false
      return true

    radio.obj_receiver = (data) ->
      _ndl3Radio.on 'object', (obj)=>
        data[objects] = [] unless data[objects]?
        data[objects].push obj

    radio.config_receiver = ->
      raw = typpo.read 'config_port_data'
      device_list = raw.get_slot 'device_list'

    radio.onReceive = (channel, callback) ->
      return false unless _init # exit if we're not initialized

      callbacks[channel] = [] unless callbacks[channel]?
      callbacks[channel].push callback
      return true

    radio.send = (channel, object) ->
      return false unless _init # exit if we're not initialized
      return false unless object?

      if _ndl3Radio
        object._channel = channel
        prefix = channel.substring 0, 2
        if prefix == 'gp'
          console.log "SENDING ON FAST PORT"
          _ndl3Radio.send(object, 'fast')
        else
          _ndl3Radio.send(object)
      else
        console.log "_ndl3Radio not defined, not sending"

    # sends an object with typpo
    sendWithTyppo = (obj, type = 'config_port', port = 'config') ->
      if not _ndl3Radio
        console.log "ndl3radio not on, not sending with typpo"
        return
      # wrap the object into binary command
      cmd = typpo.wrap(typpo.get_type(type), obj)
      # write binary command into buffer
      buf = new requireNode('buffer').Buffer(cmd.get_size())
      cmd.write(buf)
      # send buffer
      _ndl3Radio.send(buf, 'config')

    # sends the yaml-specified object obj to the config port
    sendConfig = (obj) -> sendWithTyppo(obj, 'config_port', 'config')

    radio.setGameState = (option) ->
      console.log('setting gamestate to', option)
      obj =
        id: typpo.get_const(option)
        data:
          nothing: 0 # no extra payload data
      sendConfig(obj)

    radio.sendCode = (str) ->
      console.log "transmitting robot code: " + JSON.stringify(str, null, 4)
      _ndl3Radio.send(str, 'code')

    radio.setAutonomous = ->
      this.setGameState('ID_CONTROL_SET_AUTON')

    radio.setTeleoperated = ->
      this.setGameState('ID_CONTROL_SET_TELEOP')

    radio.emergencyStop = ->
      this.setGameState('ID_CONTROL_UNPOWERED')

    return radio
])

# a service to remember things we got from the robot
.service('robotConsole', [
  ->
    robotConsole = {}
    robotConsole.output = []

    # write to the robot console (doesn't write to robot)
    robotConsole._write = (str) ->
      this.output.push str
      console.log "[Robot Print]", str

    robotConsole.lastLines = (n = 10) ->
      _.last(this.output, n)

    return robotConsole
])