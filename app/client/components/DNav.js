import React from 'react';
import {Navbar, Nav, ButtonToolbar, Button} from 'react-bootstrap';
import ReactRouterBootstrap from 'react-router-bootstrap';

export default React.createClass({
  displayName: 'DNav',
  startRobot() {
    AnsibleClient.sendMessage('execute', {});
  },
  stopRobot() {
    AnsibleClient.sendMessage('stop', {});
  },
  render() {
    return (
      <Navbar brand="Dawn" toggleNavKey={0} fixedTop fluid>
        <Nav right style={{ marginTop: '8px', marginRight: '8px' }}>
          <ButtonToolbar>
            <Button bsStyle="success" onClick={ this.startRobot }>Start</Button>
            <Button bsStyle="danger" onClick={ this.stopRobot }>Stop</Button>
          </ButtonToolbar>
        </Nav>
      </Navbar>
    );
  }
});
