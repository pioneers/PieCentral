import React from 'react';
import PropTypes from 'prop-types';
import {
  Modal,
  Button,
} from 'react-bootstrap';
import { remote } from 'electron';
import { connect } from 'react-redux';
import { addAsyncAlert } from '../actions/AlertActions';
import { pathToName, defaults, logging } from '../utils/utils';

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
    const conn = new Client();
    conn.on('ready', () => {
      conn.sftp((err, sftp) => {
        if (err) {
          logging.log(err);
        } else {
          logging.log('SSH Connection');
          sftp.fastPut(this.state.updateFilepath,
            `./updates/${update}`, (err2) => {
              if (err2) {
                conn.end();
                this.setState({ isUploading: false });
                this.props.hide();
                this.props.onAlertAdd(
                  'Robot Connectivity Error',
                  `Dawn was unable to upload the update to the robot
                  Please check your robot connectivity.`,
                );
                logging.log(err2);
              } else {
                conn.exec('sudo -H /home/ubuntu/bin/update.sh && sudo systemctl restart runtime.service',
                  { pty: true }, (uperr, stream) => {
                    if (uperr) {
                      this.props.onAlertAdd(
                        'Update Script Error',
                        `Dawn was unable to run update scripts.
                        Please check your robot connectivity.`,
                      );
                    }
                    stream.write(`${defaults.PASSWORD}\n`);
                    stream.on('exit', (code) => {
                      logging.log(`Update Script Returned ${code}`);
                      setTimeout(() => {
                        this.setState({ isUploading: false });
                        this.props.hide();
                      }, 10000);
                      conn.end();
                    });
                  });
              }
            });
        }
      });
    }).connect({
      debug: (inpt) => { logging.log(inpt); },
      host: this.props.ipAddress,
      port: defaults.PORT,
      username: defaults.USERNAME,
      password: defaults.PASSWORD,
    });
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
    let modalBody = null;
    if (this.state.isUploading) {
      modalBody = (
        <Modal.Body>
          <h4>PLEASE DO NOT TURN OFF ROBOT</h4>
          <br />
        </Modal.Body>
      );
    } else {
      modalBody = (
        <Modal.Body>
          <h4>Update Package (tar.gz file)</h4>
          <h5>{this.state.updateFilepath ? this.state.updateFilepath : ''}</h5>
          <Button type="button" onClick={this.chooseUpdate}>Choose File</Button>
          <br />
        </Modal.Body>
      );
    }
    return (
      <Modal show={this.props.shouldShow} onHide={this.props.hide}>
        <Modal.Header closeButton>
          <Modal.Title>Upload Update</Modal.Title>
        </Modal.Header>
        {modalBody}
        <Modal.Footer>
          <Button
            type="button"
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
  shouldShow: PropTypes.bool.isRequired,
  hide: PropTypes.func.isRequired,
  connectionStatus: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  isRunningCode: PropTypes.bool.isRequired,
  ipAddress: PropTypes.string.isRequired,
  onAlertAdd: PropTypes.func.isRequired,
};

const mapDispatchToProps = dispatch => ({
  onAlertAdd: (heading, message) => {
    dispatch(addAsyncAlert(heading, message));
  },
});

const UpdateBoxContainer = connect(null, mapDispatchToProps)(UpdateBox);

export default UpdateBoxContainer;
