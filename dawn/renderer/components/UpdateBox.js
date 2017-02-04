import React from 'react';
import {
  Modal,
  Button,
} from 'react-bootstrap';
import { remote } from 'electron';
import { pathToName } from '../utils/utils';

const dialog = remote.dialog;
const Client = require('ssh2').Client;

class UpdateBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isUploading: false,
      updateFilepath: '',
    };
    this.chooseUpdate = this.chooseUpdate.bind(this);
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

  upgradeSoftware() {
    this.setState({ isUploading: true });
    const update = pathToName(this.state.updateFilepath);
    if (!update) {
      this.setState({ isUploading: false });
      dialog.showMessageBox({
        type: 'warning',
        buttons: ['Close'],
        title: 'File Issue',
        message: 'Update File Bad\n',
      });
      return;
    }
    const conn = new Client();
    conn.on('ready', () => {
      conn.sftp((err, sftp) => {
        if (err) throw err;
        console.log('SSH Connection');
        sftp.fastPut(this.state.updateFilepath,
          `./updates/${update}`, (err2) => {
            if (err2) {
              dialog.showMessageBox({
                type: 'warning',
                buttons: ['Close'],
                title: 'Upload Issue',
                message: 'Update File Upload Failed.',
              });
              throw err2;
            }
          });
      });
    }).connect({
      debug: (inpt) => { console.log(inpt); },
      host: this.props.ipAddress,
      port: this.props.port,
      username: this.props.username,
      password: this.props.password,
    });
    setTimeout(() => {
      conn.end();
      this.setState({ isUploading: false });
      this.props.hide();
    }, 5000);
  }

  disableUploadUpdate() {
    return (
      !(this.state.updateFilepath) ||
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
          <br />
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
  connectionStatus: React.PropTypes.bool.isRequired,
  runtimeStatus: React.PropTypes.bool.isRequired,
  isRunningCode: React.PropTypes.bool.isRequired,
  ipAddress: React.PropTypes.string.isRequired,
  port: React.PropTypes.number.isRequired,
  username: React.PropTypes.string.isRequired,
  password: React.PropTypes.string.isRequired,
};

export default UpdateBox;
