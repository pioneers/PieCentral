import React from 'react';
import {
  Modal,
  Button,
} from 'react-bootstrap';
import { remote } from 'electron';
import Ansible from '../utils/Ansible';
const dialog = remote.dialog;

class UpdateBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isUploading: false,
      updateFilepath: '',
      signatureFilepath: '',
    };
    this.chooseUpdate = this.chooseUpdate.bind(this);
    this.chooseSignature = this.chooseSignature.bind(this);
    this.upgradeSoftware = this.upgradeSoftware.bind(this);
    this.disableUploadUpdate = this.disableUploadUpdate.bind(this);
  }

  chooseUpdate() {
    dialog.showOpenDialog({
      filters: [{ name: 'Update Package', extensions: ['gz', 'tar.gz'] }],
    }, (filepaths) => {
      if (filepaths === undefined) return;
      this.setState({ updateFilepath: filepaths[0] });
    });
  }

  chooseSignature() {
    dialog.showOpenDialog({
      filters: [{ name: 'Update signature', extensions: ['asc'] }],
    }, (filepaths) => {
      if (filepaths === undefined) return;
      this.setState({ signatureFilepath: filepaths[0] });
    });
  }

  upgradeSoftware() {
    this.setState({ isUploading: true });
    Ansible.sendMessage('pre_update', {});
    const updateP = new Promise((resolve, reject) => {
      Ansible.uploadFile(this.state.updateFilepath, (err, res) => {
        if (err) {
          reject();
        } else {
          resolve(res);
        }
      });
    });
    const signatureP = new Promise((resolve, reject) => {
      Ansible.uploadFile(this.state.signatureFilepath, (err, res) => {
        if (err) {
          reject();
        } else {
          resolve(res);
        }
      });
    });
    Promise.all([updateP, signatureP]).then((values) => {
      Ansible.sendMessage('update', {
        update_path: values[0].text,
        signature_path: values[1].text,
      });
      this.setState({ isUploading: false });
      this.props.hide();
    });
  }

  disableUploadUpdate() {
    return (
      !(this.state.updateFilepath && this.state.signatureFilepath) ||
      this.state.isUploading ||
      !(this.props.connectionStatus && this.props.runtimeStatus) ||
      this.props.isRunningCode
    );
  }

  render() {
    return (
      <Modal show={this.props.shouldShow} onHide={this.props.hide}>
        <Modal.Header closeButton>
          <Modal.Title>Upload Update</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <h4>Update Package (tar.gz file)</h4>
          <h5>{this.state.updateFilepath ? this.state.updateFilepath : ''}</h5>
          <Button onClick={this.chooseUpdate}>Choose File</Button>
          <h4>Update Signature (tar.gz.asc file)</h4>
          <h5>{this.state.signatureFilepath ? this.state.signatureFilepath : ''}</h5>
          <Button onClick={this.chooseSignature}>Choose File</Button>
          <br />
          <strong>
            Warning: This process will take a few minutes and will disconnect you from the robot.
          </strong>
        </Modal.Body>
        <Modal.Footer>
          <Button
            bsStyle="primary"
            onClick={this.upgradeSoftware}
            disabled={this.disableUploadUpdate()}
          >
            {this.state.isUploading ? 'Uploading...' : 'Upload Files'}
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }
}

UpdateBox.propTypes = {
  shouldShow: React.PropTypes.bool.isRequired,
  hide: React.PropTypes.func.isRequired,
  connectionStatus: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  isRunningCode: React.PropTypes.bool,
};

export default UpdateBox;
