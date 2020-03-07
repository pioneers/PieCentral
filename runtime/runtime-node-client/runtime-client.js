'use strict';

const zmq = require('zeromq');
const { Radio, Dish } = require('zeromq/draft');
const msgpack = require('@msgpack/msgpack');

class RuntimeClient {
  constructor(host, socket_config) {
    this.host = host;
    this.socketConfigs = {
      datagramSend: {protocol: 'udp', port: 6000, type: Radio},
      datagramRecv: {protocol: 'udp', port: 6001, type: Dish},
      command: {protocol: 'tcp', port: 6002, type: zmq.Request},
      log: {protocol: 'tcp', port: 6003, type: zmq.Subscriber},
    };
    this.sockets = {};
    this.bytes_sent = this.bytes_recv = this.messageId = 0;
    this.copy = true;
  }

  _getAddress(protocol, port, host) {
    return `${protocol}://${host || this.host}:${port}`;
  }

  async _send(name, payload) {
    let packet = msgpack.encode(payload);
    this.bytes_sent += packet.length;
    let socket = this.sockets[name];
    if (this.socketConfigs[name].type === Radio) {
      return await socket.send(packet, { group: '' });
    }
    return await socket.send(packet);
  }

  async *_recv(name) {
    for await (const [packet] of this.sockets[name]) {
      this.bytes_recv += packet.length;
      yield msgpack.decode(packet);
    }
  }

  async sendDatagram(gamepads, host) {
    let gamepadData = {};
    for (const index of Object.keys(gamepads)) {
      let gamepad = gamepads[index];
      gamepadData[index] = {
        lx: gamepad.joystick_left_x,
        ly: gamepad.joystick_left_y,
        rx: gamepad.joystick_right_x,
        ry: gamepad.joystick_right_y,
      };
      let buttonMap = 0x0000;
      for (const [offset, name] of RuntimeClient.BUTTONS.entries()) {
        if (gamepad[name]) {
          buttonMap |= (1 << offset);
        }
      }
      gamepadData[index].btn = buttonMap;
    }

    let payload = { gamepads: gamepadData };
    if (host) {
      let { protocol, port } = this.socketConfigs.datagramRecv;
      payload.src = this._getAddress(protocol, port, host);
    }
    return await this._send('datagramSend', payload);
  }

  recvDatagrams() {
    return this._recv('datagramRecv');
  }

  async sendCommand(commandName, args) {
    let messageId = (this.messageId + 1)%Math.pow(2, 32);
    this.messageId = messageId;
    let payload = [RuntimeClient.REQUEST, messageId, commandName, args || []];
    await this._send('command', payload);
    for await (const [resType, resId, error, result] of this._recv('command')) {
      if (resType !== RuntimeClient.RESPONSE) {
        throw Error('Received malformed response');
      } else if (resId !== messageId) {
        throw Error(`Response message ID did not match (expected: ${messageId}, actual: ${resId})`);
      } else if (error) {
        throw Error(`Received error from server: ${error}`);
      }
      return result;
    }
  }

  recvLogs() {
    return this._recv('log');
  }

  async connect(name, { protocol, port, type }, localhost = '127.0.0.1') {
    const socket = this.sockets[name] = new type();
    let address;
    if (type === Dish) {
      address = this._getAddress(protocol, port, localhost);
      await socket.bind(address);
    } else {
      address = this._getAddress(protocol, port);
      socket.connect(address);
    }
    if (type === zmq.Subscriber) {
      socket.subscribe('');
    }
    if (type === Dish) {
      socket.join('');
    }
  }

  async connectAll() {
    for (const name of Object.keys(this.socketConfigs)) {
      await this.connect(name, this.socketConfigs[name]);
    }
  }

  close(name) {
    let socket = this.sockets[name];
    delete this.sockets[name];
    socket.close();
  }

  closeAll() {
    for (const name of Object.keys(this.sockets)) {
      this.close(name);
    }
  }
}

RuntimeClient.REQUEST = 0;
RuntimeClient.RESPONSE = 1;
RuntimeClient.BUTTONS = [
  'button_a',
  'button_b',
  'button_x',
  'button_y',
  'l_bumper',
  'r_bumper',
  'l_trigger',
  'r_trigger',
  'button_back',
  'button_start',
  'l_stick',
  'r_stick',
  'dpad_up',
  'dpad_down',
  'dpad_left',
  'dpad_right',
  'button_xbox',
];
module.exports = RuntimeClient;
