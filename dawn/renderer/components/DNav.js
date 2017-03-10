import React from 'react';
import {
  Navbar,
  ButtonToolbar,
  ButtonGroup } from 'react-bootstrap';
import { remote } from 'electron';
import smalltalk from 'smalltalk';
import ConfigBox from './ConfigBox';
import UpdateBox from './UpdateBox';
import StatusLabel from './StatusLabel';
import TooltipButton from './TooltipButton';

const storage = remote.require('electron-json-storage');

class DNav extends React.Component {
  static saveAddress(currentAddress) {
    const prompt = smalltalk.prompt(
      'Enter the IP address of the robot:',
      'Examples: 192.168.13.100, 127.0.0.1',
      currentAddress,
    );
    prompt.then((value) => {
      if (/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(value)) {
        storage.set('runtimeAddress', {
          address: value,
        }, (err) => {
          if (err) throw err;
        });
      } else if (value != null) {
        console.log(`Bad IP: ${value}`);
      }
    }, () => console.log('Canceled'));
  }

  constructor(props) {
    super(props);
    this.toggleUpdateModal = this.toggleUpdateModal.bind(this);
    this.toggleConfigModal = this.toggleConfigModal.bind(this);
    this.state = {
      showUpdateModal: false,
      showConfigModal: false,
    };
  }

  updateAddress() {
    storage.has('runtimeAddress').then((hasKey) => {
      if (hasKey) {
        storage.get('runtimeAddress').then((data) => {
          this.saveAddress(data.address);
        });
      } else {
        this.saveAddress('192.168.13.100');
      }
    });
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
        <ConfigBox
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
          <Navbar.Text>
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
