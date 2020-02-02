'use strict';

const zmq = require('zeromq');
const { Radio, Dish } = require('zeromq/draft');
const msgpack = require('@msgpack/msgpack');
const _ = require('lodash');

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
    this.bytes_sent = this.bytes_recv = this.message_id = 0;
    this.copy = true;
  }

  _getAddress(protocol, port) {
    // FIXME
    return `${protocol}://${this.host}:${port}`;
  }

  async connect(name, { protocol, port, type }) {
    const socket = this.sockets[name] = new type();
    const address = this._getAddress(protocol, port);
    if (type !== Dish) {
      socket.connect(address);
    } else {
      await socket.bind(address);
    }
    if (type === zmq.Subscriber) {
      socket.subscribe('');
    }
    if (type === Dish) {
      socket.join('');
    }
    console.log(`Initialized socket on ${address}`);
  }

  async connectAll() {
    for (const name of _.keys(this.socketConfigs)) {
      await this.connect(name, this.socketConfigs[name]);
    }
  }
}

async function test() {
  let client = new RuntimeClient('127.0.0.1');
  await client.connectAll();

  // TESTING
  let sock = client.sockets.command;
  await sock.send(msgpack.encode([0, 1, 'lint', []]));
  const [result] = await sock.receive();
  console.log(await msgpack.decode(result));
}

test()
  .then(() => console.log('success!'))
  .catch(console.log);
