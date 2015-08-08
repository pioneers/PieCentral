/**
 * Haxors
 */

import React from 'react';
import PeripheralList from './PeripheralList';
import Peripheral from './PeripheralList';
import RemoteRobotStore from '../stores/RemoteRobotStore';
import _ from 'lodash';

var FinalCompPeripheralList = React.createClass({
  getInitialState() {
    return {
      peripherals: []
    };
  },
  onChange() {
    this.setState({peripherals: RemoteRobotStore.getPeripherals()});
  },
  componentDidMount() {
    RemoteRobotStore.on('change', this.onChange);
    this.onChange();
  },
  componentWillUnmount() {
    RemoteRobotStore.removeListener('change', this.onChange);
  },
  render() {
    return (
      <PeripheralList header='Connected Components'>
        {_.map(this.state.peripherals, (peripheral) => <Peripheral key={peripheral.id} {...peripheral}/>)}
      </PeripheralList>
    );
  }
});

export default FinalCompPeripheralList;
