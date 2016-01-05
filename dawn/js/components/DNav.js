import React from 'react';
import {
  Navbar,
  Nav,
  ButtonToolbar,
  Button,
  Label,
  Glyphicon} from 'react-bootstrap';

export default React.createClass({
  displayName: 'DNav',
  render() {
    let batteryLabel = (
      <Navbar.Text>
        <Label bsStyle="success" id="battery-indicator">
          Battery Level: {this.props.battery}
        </Label>
      </Navbar.Text>
    );
    return (
      <Navbar fixedTop fluid>
        <Navbar.Header>
          <Navbar.Brand>
            {"Dawn" + (this.props.connection ? "" : " (disconnected)")}
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
          { this.props.connection ? batteryLabel : null }
          <Navbar.Form
            pullRight={true}>
            <ButtonToolbar>
              <Button
                bsStyle="info"
                onClick={ this.props.startTour }
                id="tour-button">
                <Glyphicon glyph="info-sign" />
              </Button>
            </ButtonToolbar>
          </Navbar.Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
});
