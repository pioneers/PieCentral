import React from 'react';
import { Modal, Button } from 'react-bootstrap';
import { ipcRenderer } from 'electron';
import Ansible from '../utils/Ansible';

class RuntimeConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
    };

    this.openModal = this.openModal.bind(this);
    this.closeModal = this.closeModal.bind(this);
  }

  componentDidMount() {
    ipcRenderer.on('show-runtime-config', () => {
      console.log('received message');
      this.openModal();
    });
  }

  openModal() {
    this.setState({ showModal: true });
  }

  closeModal() {
    this.setState({ showModal: false });
  }

  render() {
    const runtimeVersion = this.props.runtimeVersion;
    let versionInfo = null;
    if (!this.props.connectionStatus) {
      versionInfo = (
        <p>Not connected to Runtime.</p>
      );
    } else if (!runtimeVersion) {
      versionInfo = (
        <p>
          Dawn is not receiving version data from the robot.
          This may be because your robot's software is outdated.
        </p>
      );
    } else {
      versionInfo = (
        <ul>
          <li>Current runtime version: {runtimeVersion.version}</li>
          <li>Headhash: {runtimeVersion.headhash.substring(0, 8)}</li>
          <li>Modified: {runtimeVersion.modified}</li>
        </ul>
      );
    }
    return (
      <Modal show={this.state.showModal} onHide={this.closeModal}>
        <Modal.Header>
          <Modal.Title>Runtime Configuration</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p><strong>Runtime Version Information:</strong></p>
          {versionInfo}
          <p><strong>Restart the robot's runtime:</strong></p>
          <Button
            bsStyle="danger"
            onClick={() => { Ansible.restartRuntime(); }}
            disabled={!this.props.connectionStatus}
          >
            Restart
          </Button>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={this.closeModal}>Close</Button>
        </Modal.Footer>
      </Modal>
    );
  }
}

RuntimeConfig.propTypes = {
  runtimeVersion: React.PropTypes.object,
  connectionStatus: React.PropTypes.bool,
};

export default RuntimeConfig;
