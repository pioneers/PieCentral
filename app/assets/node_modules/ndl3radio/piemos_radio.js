/* jshint globalstrict: true */
"use strict";

var typpo_module = require('./factory');
var xbee = require('./xbee');

var PIEMOS_FRAMING_YAML_FILE = 'legacy_piemos_framing.yaml';

// Init Typpo
var typpo = typpo_module.make();
typpo.set_target_type('ARM');
typpo.load_type_file(path.resolve(__dirname, PIEMOS_FRAMING_YAML_FILE), false);

exports.Radio = function(address, serial_port_object) {
  this.address = address;
  this.serportObj = serial_port_object;
  if (!this.serportObj) {
    throw 'Could not find XBee serial port!';
  }
  if (!this.address) {
    throw 'Robot address not set!';
  }
};

exports.Radio.prototype.send = function(data) {

  // This radio module only supports the aged PiEMOS radio format.
  // Therefore, only the following two fields are supported.

  for (var field in data) {
    if (field != 'PiELESDigitalVals' && field != 'PiELESAnalogVals') {
      throw ('Keys besides PiELESDigitalVals and PiELESAnalogVals are ' +
             'not supported in this protocol.');
    }
  }

  var PiELESDigitalVals = data.PiELESDigitalVals || [];
  var PiELESAnalogVals = data.PiELESAnalogVals || [];

  var digitalBitfield = 0;
  for (var i = 0; i < 8; i++) {
      if (PiELESDigitalVals[i]) {
          digitalBitfield |= (1 << i);
      }
  }

  // Create initial packet
  var initial_packet = typpo.create('pier_incomingdata');
  initial_packet.set_slot('ident',
      typpo.get_const('PIER_INCOMINGDATA_IDENT'));
  // TODO(rqou): Meaningful flags?
  initial_packet.set_slot('fieldtime', 0);
  initial_packet.set_slot('flags', 0);
  initial_packet.set_slot('analog', PiELESAnalogVals);
  initial_packet.set_slot('digital', digitalBitfield);

  var buf = xbee.createPacket(initial_packet, this.address);

  this.serportObj.write(buf);
};
