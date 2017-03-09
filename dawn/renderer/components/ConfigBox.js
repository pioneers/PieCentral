import React from 'react';
import {
  Modal,
  Button,
  FormGroup,
  Form,
  FormControl,
  ControlLabel,
} from 'react-bootstrap';

import { getValidationState } from '../utils/utils';

class ConfigBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ipAddress: this.props.ipAddress,
    };
    this.saveChanges = this.saveChanges.bind(this);
    this.disableUploadUpdate = this.disableUploadUpdate.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }

  saveChanges(e) {
    e.preventDefault();
    this.props.onIPChange(this.state.ipAddress);
    this.props.hide();
  }

  handleChange(e) {
    this.setState({ ipAddress: e.target.value });
  }

  disableUploadUpdate() {
    return this.props.runtimeStatus || this.props.isRunningCode || (getValidationState(this.state.ipAddress) === 'error');
  }

  render() {
    return (
      <Modal show={this.props.shouldShow} onHide={this.props.hide}>
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
