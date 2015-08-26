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
      <Navbar brand="Dawn" fixedTop fluid toggleNavKey={0}>
        <Nav right eventKey={0} style={{ marginBottom: '4px', marginTop: '4px', marginRight: '4px'}}>
          <ButtonToolbar>
            <Button bsStyle="success" onClick={ this.startRobot }>Start</Button>
            <Button bsStyle="danger" onClick={ this.stopRobot }>Stop</Button>
          </ButtonToolbar>
        </Nav>
      </Navbar>
    );
  }
});
