import React from 'react';
import {
  Navbar,
  Nav,
  ButtonToolbar,
  Button,
  Label,
  Glyphicon} from 'react-bootstrap';
import AnsibleClient from '../utils/AnsibleClient';
import RemoteRobotStore from '../stores/RemoteRobotStore';

export default React.createClass({
  displayName: 'DNav',
  getInitialState() {
    return { battery : 0, connection: true };
  },
  updateConnection() {
    this.setState({
      connection: RemoteRobotStore.getConnectionStatus()
    });
  },
  updateBattery() {
    this.setState({ battery: RemoteRobotStore.getBatteryLevel()});
  },
  componentDidMount() {
    RemoteRobotStore.on('change', this.updateConnection);
    RemoteRobotStore.on('change', this.updateBattery);
  },
  componentWillUnmount() {
    RemoteRobotStore.removeListener('change', this.updateConnection);
    RemoteRobotStore.removeListener('change', this.updateBattery);
  },
  render() {
    return (
      <Navbar fixedTop fluid>
        <Navbar.Header>
          <Navbar.Brand>
            {"Dawn" + (this.state.connection ? "" : " (disconnected)")}
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
          <Navbar.Text>
            <Label bsStyle="success" id="battery-indicator">
              Battery Level: {this.state.battery}
            </Label>
          </Navbar.Text>
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
