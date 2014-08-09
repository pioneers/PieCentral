var SerialPort = require('serialport').SerialPort;
var radioAddr = 'AAAAAAAAAAAAAAAA';

var serialPort = new SerialPort("/dev/ttyUSB0", {
  baudrate: 57600
});

var radio = require('./radio');

var rad = new radio.Radio();

rad.connectXBee(radioAddr, serialPort);

rad.on('send_data', function (data) {
  console.log('sending data', data);
});

rad.on('data', function (data) {
  console.log('got data', data);
});

rad.on('string', function (string) {
  console.log('got string', string);
});

rad.send({'PiELESAnalogValues': [127,127,127,127,127,127,127],
          'PiELESDigitalValues': [true,true,true,true,true,true,true,true]});
