const zmq = require('zeromq'),
  msgpack = require('@ygoe/msgpack');

//This is in case we change the protocol for some reason
const type = {
    request: 0,
    reply: 1,
    notification: 2
};

/**
 *  An implementation of a client connection to
 *  a runtime server, using zeromq and msgpack.
 */
class RuntimeClient {

  /**
   * 
   * @param {string} host - IP address of Runtime (ex: 'tcp://127.0.0.1:3000') 
   */
  constructor(host) {
    this.socket = new zmq.Request;
    this.msgid = 0;
    try {
      this.socket.connect(host);
      console.log('Client NodeJS to Runtime port connected');
    } catch(error) {
      console.error(error);
    }
  }

  /**
   * Set the robot's team alliance color
   * @param {string} alliance - should be 'blue', 'gold', or 'none'
   */
  setAlliance(alliance) {
    let msg = new RequestMessage(this.msgid, 'setAlliance', [alliance]);
    this.msgid++;
    this.socket.send(msg.toSocketMessage());
    const [msg] = await this.socket.receive();
    const decodedMsg =  msgpack.deserialize(msg);
    const err = decodedMsg[2];
    if(err) {
      throw err;
    } else {
      return;
    }
  }

  /**
   * Set the robot's current operating mode
   * @param {string} mode - should be 'auto', 'teleop', 'idle', or 'estop'
   */
  setMode(mode) {
    let msg = new RequestMessage(this.msgid, 'setMode', [mode]);
    this.msgid++;
    this.socket.send(msg.toSocketMessage());
    const [msg] = await this.socket.receive();
    const decodedMsg =  msgpack.deserialize(msg);
    const err = decodedMsg[2];
    if(err) {
      throw err;
    } else {
      return;
    }
  }

  /**
   * Set the starting zone of the robot
   * @param {string} zone - should be 'left', 'right', or 'none'
   */
  setStartingZone(zone) {
    let msg = new RequestMessage(this.msgid, 'setStartingZone', [zone]);
    this.msgid++;
    this.socket.send(msg.toSocketMessage());
    const [msg] = await this.socket.receive();
    const decodedMsg =  msgpack.deserialize(msg);
    const err = decodedMsg[2];
    if(err) {
      throw err;
    } else {
      return;
    }
  }

  /**
   * Run the robot's coding challenge solution
   * @param {int} seed - the seed for the challenge
   * @param {int} timeout - how long to wait for the code to finish 
   */
  runCodingChallenge(seed, timeout = 'something') {
    let msg = new RequestMessage(this.msgid, 'runCodingChallenge', [seed, timeout]);
    this.msgid++;
    this.socket.send(msg.toSocketMessage());
    const [msg] = await this.socket.receive();
    const decodedMsg =  msgpack.deserialize(msg);
    const returnVal = decodedMsg[3];
    if(returnVal != null) {
      return returnVal;
    } else {
      throw decodedMsg[2];
    }
  }

  /**
   * Get a mapping of UIDs to names for all devices
   * on the robot
   */
  listDeviceNames() {
    let msg = new RequestMessage(this.msgid, 'listDeviceNames', []);
    this.msgid++;
    this.socket.send(msg.toSocketMessage());
    const [msg] = await this.socket.receive();
    const decodedMsg =  msgpack.deserialize(msg);
    const returnVal = decodedMsg[3];
    if(returnVal != null) {
      return returnVal;
    } else {
      throw decodedMsg[2];
    }
  }

  /**
   * Set the name of the device with the passed in UID
   * @param {string} uid - the UID of the device you want to name
   * @param {string} name - the desired name of the device
   */
  setDeviceName(uid, name) {
    let msg = new RequestMessage(this.msgid, 'setDeviceName', [uid, name]);
    this.msgid++;
    this.socket.send(msg.toSocketMessage());
    const [msg] = await this.socket.receive();
    const decodedMsg =  msgpack.deserialize(msg);
    const err = decodedMsg[2];
    if(err) {
      throw err;
    } else {
      return;
    }
  }

  /**
   * Delete a device with the given UID
   * @param {string} uid - the UID of the device to be deleted
   */
  delDeviceName(uid) {
    let msg = new RequestMessage(this.msgid, 'delDeviceName', [uid]);
    this.msgid++;
    this.socket.send(msg.toSocketMessage());
    const [msg] = await this.socket.receive();
    const decodedMsg =  msgpack.deserialize(msg);
    const err = decodedMsg[2];
    if(err) {
      throw err;
    } else {
      return;
    }
  }
}

/**
 * A representation of a request
 * message to runtime. Should NOT 
 * be used
 */
class RequestMessage {
  constructor(msgid, method, params) {
    this.msg = [type.request, msgid, method, params];
  }

  toSocketMessage() {
    return msgpack.serialize(this.msg);
  }

  toString() {
    return this.msg.toString();
  }

  type() {
    return this.msg[0];
  }

  msgid() {
    return this.msg[1];
  }

  method() {
    return this.msg[2];
  }

  params() {
    return this.msg[3];
  }
}




//The hostname used during testing, likely to change
client = new RuntimeClient('tcp://127.0.0.1:3000');
console.log(client);