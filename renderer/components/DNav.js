import React from 'react';
import {
  Navbar,
  ButtonToolbar,
  ButtonGroup,
  Tooltip,
  OverlayTrigger,
  Button,
  Glyphicon,
} from 'react-bootstrap';
import UpdateBox from './UpdateBox';
import StatusLabel from './StatusLabel';
import { remote } from 'electron';
import smalltalk from 'smalltalk';
import Ansible from '../utils/Ansible';
const storage = remote.require('electron-json-storage');

class DNav extends React.Component {
  constructor(props) {
    super(props);
    this.state = { showUpdateModal: false };
    this.updateAddress = this.updateAddress.bind(this);
    this.getDawnVersion = this.getDawnVersion.bind(this);
    this.IPvalidate = this.IPvalidate.bind(this);
    this.saveAddress = this.saveAddress.bind(this);
    this.toggleUpdateModal = this.toggleUpdateModal.bind(this);
  }

  getDawnVersion() {
    return VERSION;
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

  IPvalidate(address) {
    return /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(address);
  }

  saveAddress(currentAddress) {
    const prompt = smalltalk.prompt(
      'Enter the IP address of the robot:',
      'Examples: 192.168.13.100, 127.0.0.1',
      currentAddress
    );
    prompt.then((value) => {
      if (/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(value)) {
        storage.set('runtimeAddress', {
          address: value,
        }, (err) => {
          if (err) throw err;
          Ansible.reload();
        });
      } else if (value != null) {
        console.log(`Bad IP: ${value}`);
      }
    }, () => console.log('Canceled'));
  }

  toggleUpdateModal() {
    this.setState({ showUpdateModal: !this.state.showUpdateModal });
  }

  render() {
    return (
      <Navbar fixedTop fluid>
        <UpdateBox
          isRunningCode={this.props.isRunningCode}
          connectionStatus={this.props.connection}
          runtimeStatus={this.props.runtimeStatus}
          shouldShow={this.state.showUpdateModal}
          hide={this.toggleUpdateModal}
        />
        <Navbar.Header>
          <Navbar.Brand id="header-title">
            {`Dawn v${this.getDawnVersion()}`}
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
          <Navbar.Form>
            <ButtonToolbar>
              <ButtonGroup>
                <OverlayTrigger
                  placement="bottom"
                  overlay={
                    <Tooltip id={'update-address-tooltip'}>
                      Robot IP
                    </Tooltip>
                  }
                >
                  <Button
                    bsStyle="info"
                    onClick={this.updateAddress}
                    id="update-address-button"
                  >
                    <Glyphicon glyph="transfer" />
                  </Button>
                </OverlayTrigger>
                <OverlayTrigger
                  placement="bottom"
                  overlay={
                    <Tooltip id={'upgrade-software-tooltip'}>
                      Upload Upgrade
                    </Tooltip>
                  }
                >
                  <Button
                    bsStyle="info"
                    onClick={this.toggleUpdateModal}
                    id="update-software-button"
                  >
                    <Glyphicon glyph="cloud-upload" />
                  </Button>
                </OverlayTrigger>
              </ButtonGroup>
            </ButtonToolbar>
          </Navbar.Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
}

DNav.propTypes = {
  isRunningCode: React.PropTypes.bool,
  connection: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  battery: React.PropTypes.number,
};

export default DNav;
