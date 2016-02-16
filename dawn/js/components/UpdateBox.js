import React from 'react';
import fs from 'fs';
import {
  Modal,
  Button
} from 'react-bootstrap';
import { remote } from 'electron';
import async from 'async';
import Ansible from '../utils/Ansible';
const dialog = remote.dialog;

export default React.createClass({
  propTypes: {
    shouldShow: React.PropTypes.bool.isRequired,
    hide: React.PropTypes.func.isRequired
  },
  getInitialState() {
    return {
      isUploading: false,
      updateFilepath: '',
      signatureFilepath: ''
    };
  },
  chooseUpdate() {
    dialog.showOpenDialog({
      filters: [{ name: 'Update Package', extensions: ['tar.gz'] }]
    }, (filepaths)=>{
      if (filepaths === undefined) return;
      this.setState({ updateFilepath: filepaths[0] });
    });
  },
  chooseSignature() {
    dialog.showOpenDialog({
      filters: [{ name: 'Update signature', extensions: ['tar.gz.asc'] }]
    }, (filepaths)=>{
      if (filepaths === undefined) return;
      this.setState({ signatureFilepath: filepaths[0] });
    });
  },
  upgradeSoftware() {
    async.map(
      [this.state.updateFilepath, this.state.signatureFilepath],
      fs.readFile, (err, results)=>{
        this.setState({isUploading: true});
        Ansible.sendMessage('update', {
          filename: this.state.updateFilepath.split('/').pop(),
          update: results[0].toString('base64'),
          signature: results[1].toString('base64')
        }, (response)=>{
          this.setState({isUploading: false});
          this.props.hide();
        });
      }
    );
  },
  render() {
    return (
      <Modal show={this.props.shouldShow} onHide={this.props.hide}>
        <Modal.Header closeButton>
          <Modal.Title>Upload Update</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <h4>Update Package (tar.gz file)</h4>
          <h5>{this.state.updateFilepath ? this.state.updateFilepath : ''}</h5>
          <Button onClick={ this.chooseUpdate }>Choose File</Button>
          <h4>Update Signature (tar.gz.asc file)</h4>
          <h5>{this.state.signatureFilepath ? this.state.signatureFilepath : ''}</h5>
          <Button onClick={ this.chooseSignature }>Choose File</Button>
          <br/>
          <strong>Warning: This process will take a few minutes and will disconnect you from the robot.</strong>
        </Modal.Body>
        <Modal.Footer>
          <Button
            bsStyle="primary"
            onClick={this.upgradeSoftware}
            disabled={!(this.state.updateFilepath && this.state.signatureFilepath) || this.state.isUploading }>
            {this.state.isUploading ? 'Uploading...' : 'Upload Files'}
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }
});
