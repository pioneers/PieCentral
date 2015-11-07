import React from 'react';
import {Navbar, Nav, ButtonToolbar, Button} from 'react-bootstrap';
import ReactRouterBootstrap from 'react-router-bootstrap';
import AnsibleClient from '../utils/AnsibleClient';
import RemoteRobotStore from '../stores/RemoteRobotStore';

export default React.createClass({
  displayName: 'DNav',
  getInitialState() {
    return { status: false };
  },
  updateStatus() {
    this.setState({ status: RemoteRobotStore.getRobotStatus() })
  },
  componentDidMount() {
    RemoteRobotStore.on('change', this.updateStatus);
  },
  componentWillUnmount() {
    RemoteRobotStore.removeListener('change', this.updateStatus);
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
            <Button bsStyle="success" onClick={ this.startRobot } disabled={this.state.status}>Start</Button>
            <Button bsStyle="danger" onClick={ this.stopRobot } disabled={!this.state.status}>Stop</Button>
          </ButtonToolbar>
        </Nav>
      </Navbar>
    );
  }
});
