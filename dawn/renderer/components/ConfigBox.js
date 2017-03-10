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
import _ from 'lodash';

import { getValidationState } from '../utils/utils';

const storage = remote.require('electron-json-storage');

class ConfigBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ipAddress: this.props.ipAddress,
      original: this.props.ipAddress,
    };
    this.saveChanges = this.saveChanges.bind(this);
    this.disableUploadUpdate = this.disableUploadUpdate.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleClose = this.handleClose.bind(this);
  }

  componentDidMount() {
    storage.get('ipAddress', (err, data) => {
      if (err) {
        console.log(err);
      } else if (!_.isEmpty(data)) {
        this.props.onIPChange(data);
        this.setState({ ipAddress: data });
      }
    });
    this.setState({ original: this.state.ipAddress });
  }

  saveChanges(e) {
    e.preventDefault();
    this.props.onIPChange(this.state.ipAddress);
    this.setState({ original: this.state.ipAddress });
    storage.set('ipAddress', this.state.ipAddress , (err) => {
      if (err) console.log(err);
    });
    this.props.hide();
  }

  handleChange(e) {
    this.setState({ ipAddress: e.target.value });
  }

  handleClose() {
    this.setState({ ipAddress: this.state.original });
    this.props.hide();
  }

  disableUploadUpdate() {
    return (getValidationState(this.state.ipAddress) === 'error');
  }

  render() {
    return (
      <Modal show={this.props.shouldShow} onHide={this.handleClose}>
        <Form action="" onSubmit={this.saveChanges}>
          <Modal.Header closeButton>
            <Modal.Title>Configuration</Modal.Title>
          </Modal.Header>
          <Modal.Body>
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
              disabled={this.disableUploadUpdate()}
            >
              Update
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    );
  }
}

ConfigBox.propTypes = {
  shouldShow: React.PropTypes.bool.isRequired,
  hide: React.PropTypes.func.isRequired,
  connectionStatus: React.PropTypes.bool.isRequired,
  runtimeStatus: React.PropTypes.bool.isRequired,
  isRunningCode: React.PropTypes.bool.isRequired,
  ipAddress: React.PropTypes.string.isRequired,
  onIPChange: React.PropTypes.func.isRequired,
};

export default ConfigBox;
