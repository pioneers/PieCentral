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
    piemos = requireNode('ndl3radio/piemos')

    typpo = typpo_module.make()
    typpo.set_target_type('ARM')
    typpo.load_type_file(RADIO_PROTOCOL_YAML_FILE, false)

    _radioAddr = ''
    _portPath = ''
    _serialPort = undefined

    radio.init = (radioAddr, portPath) ->
      _init = true
      _radioAddr = radioAddr

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
      _ndl3Radio.on('string', (str) -> robotConsole._print(str))

    radio.close = ->
      if _init
        _ndl3Radio.close() if _ndl3Radio?
        _serialPort.close() if _serialPort?
        _ndl3Radio = undefined
        _serialPort = undefined
      _init = false
      return true

    radio.callbacks = {} #keep track of callbacks to be used by listeners
    radio.sensorList = {}
    radio.sensorCount = 0

    #convert 64 bit data representation to a string
    readUInt64 = (buff, offset) ->
      return [i.toString(16) for i in buff.slice(offset, offset + 8)].join("")

    #should be called once to set up all _ndl3Radio listeners
    radio.setupListeners = () ->
      _ndl3Radio.on 'config', (buf) =>
        config_port = typpo.read 'config_port', buf
        if config_port.get_slot('id').val == typpo.get_const 'ID_DEVICE_GET_LIST'
          config_port_data = config_port.get_slot 'data'
          device_list = config_port_data.get_slot 'device_list'
          dids_raw = device_list.get_slot('dids').unwrap()
          #convert each raw did into a string
          dids = []
          for did_raw in dids_raw
            dids.push(readUInt64(did_raw.buffer, 0))
          radio.sensorCount = dids.length
          #send a descriptor request for each did
          for did in dids
            radio.sensorList[did] = ''
            descObj =
              id: typpo.get_const 'ID_DEVICE_READ_DESCRIPTOR'
              data:
                did: did  
            sendConfig descObj

        else if config_port.get_slot('id').val == typpo.get_const 'ID_DEVICE_READ_DESCRIPTOR'
          config_port_data = config_port.get_slot 'data'
          description = config_port_data.get_slot('device_read_descriptor_resp').get_slot('data').unwrap()
          did_raw = config_port_data.get_slot('device_read_descriptor_resp').get_slot('did').unwrap()
          did = readUInt64(did_raw.buffer, 0)
          radio.sensorList[did] = description
          radio.sensorCount = radio.sensorCount - 1
          #if descriptions have been added for every sensor, apply callback
          if radio.sensorCount == 0
            radio.callbacks.enumerate radio.sensorList
            radio.sensorList = {}
            radio.sensorCount = 0            

    #sends initial request for enumerating sensors 
    radio.enumerateSensors = (callback) ->
      radio.callbacks.enumerate = callback

      obj =
        id: typpo.get_const 'ID_DEVICE_GET_LIST'
        data: 
          nothing: 0

      sendConfig obj

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

    radio.sendPiEMOS = (gamepad) ->
      buttons = []
      for b in gamepad.buttons
        buttons.push(b.value)
      _ndl3Radio.emit('send_data', piemos.format_packet(_radioAddr, gamepad.axes, buttons))

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
    eventEmitter = new EventEmitter();
    robotConsole.output = []

    # write to the robot console (doesn't write to robot)
    robotConsole._print = (str) ->
      this.output.push str
      console.log "[Robot Print]", str
      eventEmitter.trigger('print', [str])

    robotConsole.lastLines = (n = 10) ->
      _.last(this.output, n)

    robotConsole.on = (callback) ->
      eventEmitter.on('print', callback)
    robotConsole.off = (callback) ->
      eventEmitter.off('print', callback)

    return robotConsole
])
