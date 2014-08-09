/* jshint globalstrict: true */
"use strict";

var typpo_module = require('./factory');
var buffer = require('buffer');
var xbee = require('./xbee');
var path = require('path');

var XBEE_FRAMING_YAML_FILE = 'xbee_typpo.yaml';
var PIEMOS_FRAMING_YAML_FILE = 'legacy_piemos_framing.yaml';

// Init Typpo
var typpo = typpo_module.make();
typpo.set_target_type('ARM');
typpo.load_type_file(path.resolve(__dirname, XBEE_FRAMING_YAML_FILE), false);
typpo.load_type_file(path.resolve(__dirname, PIEMOS_FRAMING_YAML_FILE), false);

exports.sendPacketizedData = function(serportObj, address, data) {

    var rxbuf = new buffer.Buffer(0);
    // TODO(rqou): Refactor this
    serportObj.on('data', function(data) {
        var new_rxbuf = new buffer.Buffer(rxbuf.length + data.length);
        rxbuf.copy(new_rxbuf);
        rxbuf.copy(data, rxbuf.length);
        rxbuf = new_rxbuf;
        if (!xbee.isFullPacket(rxbuf)) {
          return;
        }
        var rx_packet =
            typpo.read('xbee_api_packet', buffer.Buffer(rxbuf)).unwrap();
        var checksum = xbee.computeChecksum(
            rx_packet.payload.bytes, 0, rx_packet.length);
        if (rx_packet.payload.bytes[rx_packet.length] !== checksum) {
            return;
        }
        if (rx_packet.xbee_api_magic != typpo.get_const('XBEE_MAGIC')) {
            return;
        }
        if (rx_packet.payload.xbee_api_type !=
            typpo.get_const('XBEE_API_TYPE_RX64')) {
            return;
        }

        if (rx_packet.payload.rx64.data[0] ===
            typpo.get_const('TENSHI_NAIVE_BULK_CHUNKREQ_IDENT')) {
            var chunkreq = typpo.read('tenshi_bulk_chunkreq',
                buffer.Buffer(rx_packet.payload.rx64.data)).unwrap();
            // TODO(rqou): Stream id?

            // Create reply packet
            var initial_packet = typpo.create('tenshi_bulk_chunk');
            initial_packet.set_slot('ident',
                typpo.get_const('TENSHI_NAIVE_BULK_CHUNK_IDENT'));
            // TODO(rqou): Meaningful stream IDs
            initial_packet.set_slot('stream_id', 0);
            initial_packet.set_slot('start_addr', chunkreq.start_addr);
            initial_packet.set_slot('end_addr', chunkreq.end_addr);
            var chunklen = chunkreq.end_addr - chunkreq.start_addr;
            // TODO(rqou): This isn't efficient?
            var replyChunk = buffer.Buffer(chunklen);
            for (var i = chunkreq.start_addr; i < chunkreq.end_addr; i++) {
                replyChunk[i - chunkreq.start_addr] = data[i];
            }
            initial_packet.set_slot('data', replyChunk);

            var buf = xbee.createPacket(initial_packet, address);

            serportObj.write(buf);
        }
        else if (rx_packet.payload.rx64.data[0] ===
            typpo.get_const('TENSHI_NAIVE_BULK_STOP_IDENT')) {

            // TODO(rqou): Do something here? Waiting for done?
        }
    });

    // Create initial packet
    var initial_packet = typpo.create('tenshi_bulk_start');
    initial_packet.set_slot('ident',
        typpo.get_const('TENSHI_NAIVE_BULK_START_IDENT'));
    // TODO(rqou): Meaningful stream IDs
    initial_packet.set_slot('stream_id', 0);
    initial_packet.set_slot('length', data.length);

    var buf = xbee.createPacket(initial_packet, ROBOT);

    serportObj.write(buf);
};
