angular.module('daemon.read_descriptor', [])

.service('read_descriptor', [
  ->
    buffer = requireNode("buffer")
    readString = (buf, startIndex) ->
      length = buf.readUInt8(startIndex)
      
      #console.log(length)
      description = buf.slice(startIndex + 1, length + startIndex + 1)
      [
        description.toString("utf8")
        length + startIndex + 1
      ]

    readChannelDescriptor = (buf, startIndex) ->
      descriptors = []
      index = startIndex + 1 
      numChannels = buf.readUInt8(startIndex)
      i = 0

      while i < numChannels
        channelDescriptor = readString(buf, index + 1)
        type = buf.readUInt8(channelDescriptor[1]) 
        typeData = typeChannel(buf, type, channelDescriptor[1] + 1)
        descriptors.push [
          channelDescriptor[0]
          typeData[0]
        ]
        index = typeData[1]
        i++
      descriptors

    typeChannel = (buf, typeBinary, startIndex) ->
      FLAGS_LENGTH = 1
      SAMPLE_RATE_LENGTH = 2
      BIT_PER_SAMPLE_LENGTH = 1
      INTERNAL_TIMER_TICK_FREQ_LENGTH = 4
      INTERNAL_CYCLE_TIME_TICK_LENGTH = 4
      MODE = 1
      SPEED = 4
      numTotal = startIndex
      typeString = ""
      switch typeBinary
        when 0x00
          numTotal += FLAGS_LENGTH + SAMPLE_RATE_LENGTH
          typeString = "Digital In/Out"
        when 0x01
          num = numTotal + SAMPLE_RATE_LENGTH + BIT_PER_SAMPLE_LENGTH
          numTotal = calibrationType(buf, num)
          typeString = "Analog Input"
        when 0x02
          num = numTotal + SAMPLE_RATE_LENGTH + BIT_PER_SAMPLE_LENGTH
          numTotal = calibrationType(buf, num)
          typeString = "Analog Output"
        when 0x03
          num = numTotal + BIT_PER_SAMPLE_LENGTH + INTERNAL_TIMER_TICK_FREQ_LENGTH + INTERNAL_CYCLE_TIME_TICK_LENGTH
          numTotal = calibrationType(buf, num)
          typeString = "Hobby Servo"
        when 0x40 # TODO(Matt Zhao): Implement when these are implemented
          typeString = "Generic I2C"
        when 0x41 # TODO(Matt Zhao): Implement when these are implemented
          typeString = "Generic SPI"
        when 0x42 # TODO(Matt Zhao): Implement when these are implemented
          typeString = "Generic UART"
        when 0x80
          numTotal += MODE + SPEED
          typeString = "Grizzly Bear v3"
        when 0x81 # TODO(Matt Zhao): change when battery buzzer additional info block changed
          num = numTotal + SAMPLE_RATE_LENGTH + BIT_PER_SAMPLE_LENGTH
          numTotal = calibrationType(buf, num)
          typeString = "Battery Buzzer"
        when 0x82 # TODO(Matt Zhao): change when team flag additional info block changed
          numTotal += FLAGS_LENGTH + SAMPLE_RATE_LENGTH
          typeString = "Team Flag"
        when 0xfe
          # numTotal += MODE;
          # TODO(Matt Zhao): Uncomment previous line if firmware is fixed
          typeString = "Actuator Mode"
        when 0xff #no calibration data present
          typeString = "debugger"
      [
        typeString
        numTotal
      ]

    calibrationType = (buf, startIndex) ->
      type = buf.readUInt8(startIndex)
      numTotal = startIndex + 1
      FLOAT_LENGTH = 4
      COUNT_ENTRIES_LENGTH = 4
      switch type
        when 0x00
          numTotal += 0
        when 0x01
          numTotal += 2 * FLOAT_LENGTH
        when 0x02
          numTotal += 3 * FLOAT_LENGTH
        when 0x03
          numTotal += 3 * FLOAT_LENGTH
        when 0x04
          countEntries = buf.readUInt32LE(numTotal)
          numTotal += COUNT_ENTRIES_LENGTH + countEntries * 2 * FLOAT_LENGTH
      numTotal

    return readChannelDescriptor
])
