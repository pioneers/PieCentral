import React from 'react';
import PropTypes from 'prop-types';
import {
  Modal,
  Button,
  FormGroup,
  Form,
  FormControl,
  ControlLabel,
} from 'react-bootstrap';
import { remote, ipcRenderer } from 'electron';
import { connect } from 'react-redux';
import _ from 'lodash';
import { getValidationState, logging } from '../utils/utils';
import { updateFieldControl } from '../actions/FieldActions';
import { ipChange } from '../actions/InfoActions';


const storage = remote.require('electron-json-storage');

class ConfigBoxComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ipAddress: this.props.ipAddress,
      fcAddress: this.props.fcAddress,
      stationNumber: this.props.stationNumber,
      originalIP: this.props.ipAddress,
      originalSN: this.props.stationNumber,
      originalFC: this.props.fcAddress,
    };
    this.saveChanges = this.saveChanges.bind(this);
    this.disableUploadUpdate = this.disableUploadUpdate.bind(this);
    this.handleIpChange = this.handleIpChange.bind(this);
    this.handleFcChange = this.handleFcChange.bind(this);
    this.handleStationChange = this.handleStationChange.bind(this);
    this.handleClose = this.handleClose.bind(this);
  }

  componentDidMount() {
    storage.get('ipAddress', (err, data) => {
      if (err) {
        logging.log(err);
      } else if (!_.isEmpty(data)) {
        this.props.onIPChange(data);
        this.setState({
          ipAddress: data,
          originalIP: data,
        });
      }
    });

    storage.get('fieldControl', (err, data) => {
      if (err) {
        logging.log(err);
      } else if (!_.isEmpty(data)) {
        const sn = data.stationNumber;
        const ba = data.bridgeAddress;
        this.setState({
          fcAddress: ba,
          originalFC: ba,
          stationNumber: sn,
          originalSN: sn,
        });
      }
    });
  }

  saveChanges(e) {
    e.preventDefault();
    this.props.onIPChange(this.state.ipAddress);
    this.setState({ originalIP: this.state.ipAddress });
    storage.set('ipAddress', this.state.ipAddress, (err) => {
      if (err) logging.log(err);
    });

    const newConfig = {
      stationNumber: this.state.stationNumber,
      bridgeAddress: this.state.fcAddress,
    };
    this.props.onFCUpdate(newConfig);
    this.setState({
      originalSN: this.state.stationNumber,
      originalFC: this.state.fcAddress,
    });
    storage.set('fieldControl', newConfig, (err) => {
      if (err) logging.log(err);
    });
    ipcRenderer.send('LCM_CONFIG_CHANGE', newConfig);

    this.props.hide();
  }

  handleIpChange(e) {
    this.setState({ ipAddress: e.target.value });
  }

  handleFcChange(e) {
    this.setState({ fcAddress: e.target.value });
  }

  handleStationChange(e) {
    this.setState({ stationNumber: e.target.value });
  }

  handleClose() {
    this.setState({ ipAddress: this.state.originalIP });
    this.props.hide();
  }

  disableUploadUpdate() {
    return (getValidationState(this.state.ipAddress) === 'error') ||
      (getValidationState(this.state.fcAddress) === 'error') ||
      (this.state.stationNumber < 0 && this.state.stationNumber > 4);
  }

  render() {
    return (
      <Modal show={this.props.shouldShow} onHide={this.handleClose}>
        <Form action="" onSubmit={this.saveChanges}>
          <Modal.Header closeButton>
            <Modal.Title>Dawn Configuration</Modal.Title>
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
                onChange={this.handleIpChange}
              />
              <FormControl.Feedback />
            </FormGroup>

            <p>
              Field Control Settings
            </p>
            <FormGroup
              controlId="fcAddress"
              validationState={getValidationState(this.state.fcAddress)}
            >
              <ControlLabel>Field Control IP Address</ControlLabel>
              <FormControl
                type="text"
                value={this.state.fcAddress}
                placeholder="i.e. 192.168.100.13"
                onChange={this.handleFcChange}
              />
              <FormControl.Feedback />
            </FormGroup>

            <FormGroup
              controlId="stationNumber"
              validationState={(this.state.stationNumber >= 0 && this.state.stationNumber <= 4) ? 'success' : 'error'}
            >
              <ControlLabel>Field Control Station Number</ControlLabel>
              <FormControl
                type="number"
                value={this.state.stationNumber}
                placeholder="An integer from 0 to 4"
                onChange={this.handleStationChange}
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

ConfigBoxComponent.propTypes = {
  shouldShow: PropTypes.bool.isRequired,
  hide: PropTypes.func.isRequired,
  ipAddress: PropTypes.string.isRequired,
  stationNumber: PropTypes.number.isRequired,
  onIPChange: PropTypes.func.isRequired,
  fcAddress: PropTypes.string.isRequired,
  onFCUpdate: PropTypes.func.isRequired,
};

const mapDispatchToProps = dispatch => ({
  onIPChange: (ipAddress) => {
    dispatch(ipChange(ipAddress));
  },
  onFCUpdate: (config) => {
    dispatch(updateFieldControl(config));
  },
});

const mapStateToProps = state => ({
  stationNumber: parseInt(state.fieldStore.stationNumber, 10),
  fcAddress: state.fieldStore.bridgeAddress,
});

const ConfigBox = connect(mapStateToProps, mapDispatchToProps)(ConfigBoxComponent);

export default ConfigBox;
