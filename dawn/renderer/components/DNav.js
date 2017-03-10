import React from 'react';
import {
  Navbar,
  ButtonToolbar,
  ButtonGroup } from 'react-bootstrap';
import IPBox from './IPBox';
import UpdateBox from './UpdateBox';
import StatusLabel from './StatusLabel';
import TooltipButton from './TooltipButton';

class DNav extends React.Component {
  constructor(props) {
    super(props);
    this.toggleUpdateModal = this.toggleUpdateModal.bind(this);
    this.toggleConfigModal = this.toggleConfigModal.bind(this);
    this.state = {
      showUpdateModal: false,
      showConfigModal: false,
    };
  }

  toggleUpdateModal() {
    this.setState({ showUpdateModal: !this.state.showUpdateModal });
  }

  toggleConfigModal() {
    this.setState({ showConfigModal: !this.state.showConfigModal });
  }

  render() {
    return (
      <Navbar fixedTop fluid>
        <UpdateBox
          isRunningCode={this.props.isRunningCode}
          connectionStatus={this.props.connection}
          runtimeStatus={this.props.runtimeStatus}
          shouldShow={this.state.showUpdateModal}
          ipAddress={this.props.ipAddress}
          hide={this.toggleUpdateModal}
        />
        <IPBox
          isRunningCode={this.props.isRunningCode}
          connectionStatus={this.props.connection}
          runtimeStatus={this.props.runtimeStatus}
          shouldShow={this.state.showConfigModal}
          ipAddress={this.props.ipAddress}
          onIPChange={this.props.onIPChange}
          hide={this.toggleConfigModal}
        />
        <Navbar.Header>
          <Navbar.Brand id="header-title">
            {`Dawn v${VERSION}`}
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
          <Navbar.Text id="battery-indicator">
            <StatusLabel
              connectionStatus={this.props.connection}
              runtimeStatus={this.props.runtimeStatus}
              battery={this.props.battery}
            />
          </Navbar.Text>
          <Navbar.Form
            pullRight
          >
            <ButtonToolbar>
              <ButtonGroup>
                <TooltipButton
                  placement="bottom"
                  text="Tour"
                  bsStyle="info"
                  onClick={this.props.startTour}
                  id="tour-button"
                  glyph="info-sign"
                />
                <TooltipButton
                  placement="bottom"
                  text="Robot IP"
                  bsStyle="info"
                  onClick={this.toggleConfigModal}
                  id="update-address-button"
                  glyph="transfer"
                />
                <TooltipButton
                  placement="bottom"
                  text="Upload Upgrade"
                  bsStyle="info"
                  onClick={this.toggleUpdateModal}
                  disabled={this.props.runtimeStatus || this.props.isRunningCode}
                  id="update-software-button"
                  glyph="cloud-upload"
                />
              </ButtonGroup>
            </ButtonToolbar>
          </Navbar.Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
}

DNav.propTypes = {
  connection: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  battery: React.PropTypes.number,
  isRunningCode: React.PropTypes.bool,
  ipAddress: React.PropTypes.string,
  startTour: React.PropTypes.func,
  onIPChange: React.PropTypes.func,
};

export default DNav;
