/* jshint globalstrict: true */
"use strict";

var path = require('path');
var typpo_module = require('./factory');

var PIEMOS_FRAMING_YAML_FILE = path.join(__dirname, 'legacy_piemos_framing.yaml');
var XBEE_FRAMING_YAML_FILE = path.join(__dirname, 'xbee_typpo.yaml');
console.log(PIEMOS_FRAMING_YAML_FILE);
console.log(XBEE_FRAMING_YAML_FILE);

// Init Typpo
var typpo = typpo_module.make();
typpo.set_target_type('ARM');
typpo.load_type_file(PIEMOS_FRAMING_YAML_FILE, false);
typpo.load_type_file(XBEE_FRAMING_YAML_FILE, false);


module.exports = typpo;
