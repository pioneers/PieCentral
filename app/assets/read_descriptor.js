'use strict';
 
var buffer = require('buffer');

var readString = function(buf, startIndex) {
	var length = buf.readUInt8(startIndex)
	//console.log(length)
	var description = buf.slice(startIndex + 1, length + startIndex + 1)
	return [description.toString('utf8'), length + startIndex + 1]
}

var readChannelDescriptor = function(buf, startIndex) {
	var descriptors = []
	var index = startIndex + 1 //skips over the number of channel
	var numChannels = buf.readUInt8(startIndex) 
	for (var i = 0; i < numChannels; i++) {
		var channelDescriptor = readString(buf, index + 1) 
		//console.log(channelDescriptor)
		var type = buf.readUInt8(channelDescriptor[1]) //not sure if this is off by one, reading the type
		var typeData = typeChannel(buf, type, channelDescriptor[1] + 1) 
		//console.log("Type: " + typeData[0] + " Num Add: " + typeData[1]);
		descriptors.push([channelDescriptor, typeData[0]]) 
		index = typeData[1] 
	}
	return descriptors
}

var typeChannel = function(buf, typeBinary, startIndex) {
	var FLAGS_LENGTH = 1
	var SAMPLE_RATE_LENGTH = 2
	var BIT_PER_SAMPLE_LENGTH = 1
	var INTERNAL_TIMER_TICK_FREQ_LENGTH = 4
	var INTERNAL_CYCLE_TIME_TICK_LENGTH = 4
	var MODE = 1
	var SPEED = 4

	var numTotal = startIndex
	var typeString = ""

	switch (typeBinary) {
		case 0x00:
			numTotal += FLAGS_LENGTH + SAMPLE_RATE_LENGTH;
			typeString = "Digital In/Out"; 
			break;
		case 0x01:
			var num = numTotal + SAMPLE_RATE_LENGTH + BIT_PER_SAMPLE_LENGTH;
			numTotal = calibrationType(buf, num);
			typeString = "Analog Input";
			break;
		case 0x02:
			var num = numTotal + SAMPLE_RATE_LENGTH + BIT_PER_SAMPLE_LENGTH;
			numTotal = calibrationType(buf, num);
			typeString = "Analog Output";
			break;
		case 0x03:
			var num = numTotal + BIT_PER_SAMPLE_LENGTH + INTERNAL_TIMER_TICK_FREQ_LENGTH + INTERNAL_CYCLE_TIME_TICK_LENGTH;
			numTotal = calibrationType(buf, num); 
			typeString = "Hobby Servo";
			break;
		case 0x40: // TODO(Matt Zhao): Implement when these are implemented
			typeString = "Generic I2C";
			break;
		case 0x41: // TODO(Matt Zhao): Implement when these are implemented
			typeString = "Generic SPI";
			break;
		case 0x42: // TODO(Matt Zhao): Implement when these are implemented
			typeString = "Generic UART";
			break;
		case 0x80:
			numTotal += MODE + SPEED;
			typeString = "Grizzly Bear v3";
			break;
		case 0x81: // TODO(Matt Zhao): change when battery buzzer additional info block changed
			var num = numTotal + SAMPLE_RATE_LENGTH + BIT_PER_SAMPLE_LENGTH;
			numTotal = calibrationType(buf, num);
			typeString = "Battery Buzzer";
			break;
		case 0x82: // TODO(Matt Zhao): change when team flag additional info block changed
			numTotal += FLAGS_LENGTH + SAMPLE_RATE_LENGTH;
			typeString = "Team Flag";
			break;
		case 0xFE:
			// numTotal += MODE;
			// TODO(Matt Zhao): Uncomment previous line if firmware is fixed
			typeString = "Actuator Mode";
			break;
		case 0xFF: //no calibration data present
			typeString = "debugger";
			break;
	}
	return [typeString, numTotal];
}

var calibrationType = function(buf, startIndex) {
	var type = buf.readUInt8(startIndex) 
	var numTotal = startIndex + 1
	var FLOAT_LENGTH = 4
	var COUNT_ENTRIES_LENGTH = 4
	switch (type) {
		case 0x00:
			numTotal += 0;
			break;
		case 0x01:
			numTotal += 2 * FLOAT_LENGTH; 
			break;
		case 0x02:
			numTotal += 3 * FLOAT_LENGTH;
			break;
		case 0x03:
			numTotal += 3 * FLOAT_LENGTH;
			break;
		case 0x04:
			var countEntries = buf.readUInt32LE(numTotal);
			numTotal += COUNT_ENTRIES_LENGTH + countEntries * 2 * FLOAT_LENGTH; 
			break;
	}
	return numTotal;
}

// Sample Enumeration
var buf = buffer.Buffer([20, 1, 82, 84, 104, 105, 115, 32, 105, 115, 32, 97, 32, 100, 105, 103, 105, 116, 
						 97, 108, 32, 115, 101, 110, 115, 111, 114, 46, 32, 32, 73, 116, 32, 99, 97, 110, 
						 32, 98, 101, 32, 117, 115, 101, 100, 32, 116, 111, 32, 103, 101, 116, 32, 116, 
						 104, 101, 32, 115, 116, 97, 116, 101, 32, 111, 102, 32, 117, 112, 32, 116, 111, 
						 32, 102, 111, 117, 114, 32, 115, 119, 105, 116, 99, 104, 101, 115, 46, 255, 255, 
						 5, 25, 22, 84, 104, 101, 32, 103, 97, 109, 101, 32, 109, 111, 100, 101, 32, 99, 
						 104, 97, 110, 110, 101, 108, 46, 254, 40, 33, 84, 104, 105, 115, 32, 105, 115, 
						 32, 116, 104, 101, 32, 102, 105, 114, 115, 116, 32, 97, 110, 97, 108, 111, 103, 
						 32, 99, 104, 97, 110, 110, 101, 108, 46, 1, 255, 255, 255, 255, 41, 34, 84, 104, 
						 105, 115, 32, 105, 115, 32, 116, 104, 101, 32, 115, 101, 99, 111, 110, 100, 32, 
						 97, 110, 97, 108, 111, 103, 32, 99, 104, 97, 110, 110, 101, 108, 46, 1, 255, 255, 
						 255, 255, 40, 33, 84, 104, 105, 115, 32, 105, 115, 32, 116, 104, 101, 32, 116, 104, 
						 105, 114, 100, 32, 97, 110, 97, 108, 111, 103, 32, 99, 104, 97, 110, 110, 101, 108, 
						 46, 1, 255, 255, 255, 255, 41, 34, 84, 104, 105, 115, 32, 105, 115, 32, 116, 104, 
						 101, 32, 102, 111, 117, 114, 116, 104, 32, 97, 110, 97, 108, 111, 103, 32, 99, 104, 
						 97, 110, 110, 101, 108, 46, 1, 255, 255, 255, 255, 57])

var start = 2
var str = readString(buf, start)
console.log(readString(buf, start))
console.log(str[1])
var offset = 2 + str[1] 
console.log(readChannelDescriptor(buf, offset))