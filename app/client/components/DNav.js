import React from 'react';
import {Navbar, Nav, ButtonToolbar, Button, Label} from 'react-bootstrap';
import ReactRouterBootstrap from 'react-router-bootstrap';
import AnsibleClient from '../utils/AnsibleClient';
import RemoteRobotStore from '../stores/RemoteRobotStore';

export default React.createClass({
  displayName: 'DNav',
  getInitialState() {
    return { status: false , battery : 0, connection: true };
  },
  updateStatus() {
    this.setState({
      status: RemoteRobotStore.getRobotStatus(),
      connection: RemoteRobotStore.getConnectionStatus()
    });
  },
  updateBattery() {
    this.setState({ battery: RemoteRobotStore.getBatteryLevel()});
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
      <Navbar
        brand={"Dawn" + (this.state.connection ? "" : " (disconnected)")}
        fixedTop fluid toggleNavKey={0}>
        <Nav right eventKey={0} style={{ marginBottom: '4px', marginTop: '4px', marginRight: '4px'}}>
          <ButtonToolbar>
            <Label bsStyle="success" style={{ marginTop: '12px', marginRight: '15px'}}> Battery Level: {this.state.battery}</Label>
            <Button bsStyle="success" onClick={ this.startRobot } disabled={this.state.status || !this.state.connection}>Start</Button>
            <Button bsStyle="danger" onClick={ this.stopRobot } disabled={!this.state.status || !this.state.connection}>Stop</Button>
          </ButtonToolbar>
        </Nav>
      </Navbar>
    );
  }
});
