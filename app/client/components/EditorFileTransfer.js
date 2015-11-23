import React from 'react';
import { Button, ButtonGroup, Modal } from 'react-bootstrap';
import Dropzone from 'react-dropzone';
import request from 'superagent';
import EditorActionCreators from '../actions/EditorActionCreators';

var EditorFileTransfer = React.createClass({
  propTypes: {
    filename: React.PropTypes.string
  },
  getInitialState() {
    return { showModal: false };
  },
  closeModal() {
    this.setState({ showModal: false });
  },
  openModal() {
    this.setState({ showModal: true });
  },
  onDrop(files) {
    var req = request.post('/api/editor/upload');
    req.attach('file', files[0], files[0].name);
    req.end(() => {
      EditorActionCreators.getCode(this.props.filename);
      this.closeModal();
    });
  },
  render() {
    return (
      <ButtonGroup>
        <Button bsSize="small"
          href={'/api/editor/download?filename=' + this.props.filename} >
          Download
        </Button>
        <Modal show={this.state.showModal} onHide={this.closeModal}>
          <Modal.Header closeButton>
            <Modal.Title>Upload your code file.</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Dropzone
              style={{ width:'100%', height:'300px', border: '2px dashed black' }}
              onDrop={this.onDrop}
              multiple={ false }>
              <div style={{ padding: '10px 10px 10px 10px'}}>
                <h4>
                Drag and drop your code file here, or click to select the file.
                </h4>
                <p>
                  Note: The file you upload will AUTOMATICALLY OVERWRITE any
                  existing file of the same name.
                </p>
              </div>
            </Dropzone>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.closeModal}>Close</Button>
          </Modal.Footer>
        </Modal>
        <Button bsSize="small" onClick={this.openModal}>Upload</Button>
      </ButtonGroup>
    );
  }
});

export default EditorFileTransfer;
