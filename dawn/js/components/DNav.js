import React from 'react';
import {
  Navbar,
  Nav,
  ButtonToolbar,
  ButtonGroup,
  Tooltip,
  OverlayTrigger,
  Button,
  Label,
  Glyphicon} from 'react-bootstrap';
import { remote } from 'electron';
import smalltalk from 'smalltalk';

export default React.createClass({
  displayName: 'DNav',
  updateAddress() {
    let defaultAddress = localStorage.getItem('runtimeAddress') || '127.0.0.1';
    smalltalk.prompt(
      'Enter the IP address of robot/runtime:',
      'WARNING: This will reload the application. Save any changes you have.',
      defaultAddress).then((value) => {
        localStorage.setItem('runtimeAddress', value);
        remote.getCurrentWebContents().reload();
      }, ()=>console.log('Canceled'));
  },
  render() {
    return (
      <Navbar fixedTop fluid>
        <Navbar.Header>
          <Navbar.Brand>
            {"Dawn" + (this.props.connection ? "" : " (disconnected)")}
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
          <Navbar.Text>
            <Label bsStyle="success" id="battery-indicator">
              Battery Level: {
                this.props.connection ? this.props.battery : 'Not connected.'
              }
            </Label>
          </Navbar.Text>
          <Navbar.Form
            pullRight={true}>
            <ButtonToolbar>
              <ButtonGroup>
                <OverlayTrigger
                  placement="bottom"
                  overlay={
                    <Tooltip id={ 'tour-tooltip' }>
                      "Tour"
                    </Tooltip>
                  }>
                  <Button
                    bsStyle="info"
                    onClick={ this.props.startTour }
                    id="tour-button">
                    <Glyphicon glyph="info-sign" />
                  </Button>
                </OverlayTrigger>
                <OverlayTrigger
                  placement="bottom"
                  overlay={
                    <Tooltip id={ 'update-address-tooltip' }>
                      "Robot IP"
                    </Tooltip>
                  }>
                  <Button
                    bsStyle="info"
                    onClick={ this.updateAddress }
                    id = "update-address-button">
                    <Glyphicon glyph="transfer" />
                  </Button>
                </OverlayTrigger>
              </ButtonGroup>
            </ButtonToolbar>
          </Navbar.Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
});
