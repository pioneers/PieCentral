import React from 'react';
import {Navbar, Nav, ButtonToolbar, Button, Label, ButtonGroup} from 'react-bootstrap';
import ReactRouterBootstrap from 'react-router-bootstrap';
import AnsibleClient from '../utils/AnsibleClient';
import RemoteRobotStore from '../stores/RemoteRobotStore';

export default React.createClass({
  displayName: 'DNav',
  getInitialState() {
    return { status: false , battery : 0};
  },
  updateStatus() {
    this.setState({ status: RemoteRobotStore.getRobotStatus()})
  },
  updateBattery() {
    this.setState({ battery: RemoteRobotStore.getBatteryLevel()})
  },
  componentDidMount() {
    RemoteRobotStore.on('change', this.updateStatus);
    RemoteRobotStore.on('change', this.updateBattery);
  },
  componentWillUnmount() {
    RemoteRobotStore.removeListener('change', this.updateStatus);
    RemoteRobotStore.removeListener('change', this.updateBattery);
  },
  startRobot() {
    AnsibleClient.sendMessage('execute', {});
  },
  stopRobot() {
    AnsibleClient.sendMessage('stop', {});
  },
  
  render() {
    return (
      <Navbar brand="Dawn" fixedTop fluid toggleNavKey={0}>
        <Nav right eventKey={0} style={{ marginBottom: '4px', marginTop: '4px', marginRight: '4px'}}>
          <ButtonToolbar>
            <ButtonGroup>
            <Button bsStyle="success"> Battery Level: {this.state.battery}</Button>
            </ButtonGroup>
            <ButtonGroup>
            <Button bsStyle="success" onClick={ this.startRobot } disabled={this.state.status}>Start</Button>
            <Button bsStyle="danger" onClick={ this.stopRobot } disabled={!this.state.status}>Stop</Button>
            </ButtonGroup>
          </ButtonToolbar>

        </Nav>
      </Navbar>
    );
  }
});
