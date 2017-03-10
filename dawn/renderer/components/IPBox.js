import React from 'react';
import {
  Modal,
  Button,
  FormGroup,
  Form,
  FormControl,
  ControlLabel,
} from 'react-bootstrap';
import { remote } from 'electron';
import { getValidationState } from '../utils/utils';

const storage = remote.require('electron-json-storage');

class IPBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ipAddress: this.props.ipAddress,
    };
    this.saveChanges = this.saveChanges.bind(this);
    this.disableIPUpdate = this.disableIPUpdate.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.hideAndRevertIP = this.hideAndRevertIP.bind(this);
    storage.has('runtimeAddress').then((hasKey) => {
      if (hasKey) {
        storage.get('runtimeAddress').then((data) => {
          this.setState({ ipAddress: data.address });
        });
      } else {
        // state already has default value
      }
    });
  }

  saveChanges(e) {
    e.preventDefault();
    this.props.onIPChange(this.state.ipAddress);
    storage.set('runtimeAddress', {
      address: this.state.ipAddress,
    }, (err) => {
      if (err) throw err;
    });
    this.props.hide();
  }

  handleChange(e) {
    this.setState({ ipAddress: e.target.value });
  }

  disableIPUpdate() {
    return (getValidationState(this.state.ipAddress) === 'error');
  }

  hideAndRevertIP() {
    this.setState({ ipAddress: this.props.ipAddress });
    this.props.hide();
  }

  render() {
    return (
      <Modal show={this.props.shouldShow} onHide={this.hideAndRevertIP}>
        <Form action="" onSubmit={this.saveChanges}>
          <Modal.Header closeButton>
            <Modal.Title>Robot IP Address</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>
              Make sure only one computer (running instance of Dawn) is attempting
              to connect to the robot at a time! (i.e. not trying to connect to the same IP Address)
            </p>
            <FormGroup
              controlId="ipAddress"
              validationState={getValidationState(this.state.ipAddress)}
            >
              <ControlLabel>IP Address</ControlLabel>
              <FormControl
                type="text"
                value={this.state.ipAddress}
                placeholder="i.e. 192.168.100.13"
                onChange={this.handleChange}
              />
              <FormControl.Feedback />
            </FormGroup>
          </Modal.Body>
          <Modal.Footer>
            <Button
              type="submit"
              bsStyle="primary"
              disabled={this.disableIPUpdate()}
            >
              Update
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    );
  }
}

IPBox.propTypes = {
  shouldShow: React.PropTypes.bool.isRequired,
  hide: React.PropTypes.func.isRequired,
  connectionStatus: React.PropTypes.bool.isRequired,
  runtimeStatus: React.PropTypes.bool.isRequired,
  isRunningCode: React.PropTypes.bool.isRequired,
  ipAddress: React.PropTypes.string.isRequired,
  onIPChange: React.PropTypes.func.isRequired,
};

export default IPBox;
