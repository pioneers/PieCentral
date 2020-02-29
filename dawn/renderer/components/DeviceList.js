import React from 'react';
import { connect } from 'react-redux';
import {
  Card,
  EditableText,
  Icon,
} from '@blueprintjs/core';
import { IconNames } from '@blueprintjs/icons';
import { renameDevice } from '../actions/devices';

const DEVICE_TYPES = {
  LineFollower: {
    displayName: 'Line Follower',
    icon: IconNames.FLASH,
  },
  BatteryBuzzer: {
    displayName: 'Battery',
    icon: IconNames.OFFLINE,
  },
  TeamFlag: {
    displayName: 'Team Flag',
    icon: IconNames.FLAG,
  },
  ServoControl: {
    displayName: 'Servo',
    icon: IconNames.COG,
  },
  YogiBear: {
    displayName: 'Motor (Yogi Bear)',
    icon: IconNames.COG,
  },
  PolarBear: {
    displayName: 'Motor (Polar Bear)',
    icon: IconNames.COG,
  },
  RFID: {
    displayName: 'RFID',
    icon: IconNames.FEED,
  }
};

const Device = (props) => {
  const { type, uid, alias } = props.device;
  // FIXME: unknown device
  const { icon, displayName } = DEVICE_TYPES[type];
  return (
    <Card className="card">
      <span><Icon icon={icon} /> {displayName}</span>
      <div className="device-name">
        <EditableText
          className="device-alias"
          placeholder="Assign a name"
          value={alias}
          onChange={props.renameDevice}
        />
        <pre className="device-uid">{uid}</pre>
      </div>
    </Card>
  );
};

// FIXME
const DeviceList = (props) => (
  <div className="card-container devices-cards">
    {props.devices.map((device, index) => (
      <Device
        key={index}
        device={device}
        renameDevice={() => null}
      />
    ))}
  </div>
);

export default connect(
  state => ({ devices: state.devices.sensors.concat(state.devices.gamepads) }),
)(DeviceList);
