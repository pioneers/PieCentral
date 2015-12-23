import React from 'react';
import Dropzone from 'react-dropzone';
import request from 'superagent';
import EditorActionCreators from '../actions/EditorActionCreators';
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Panel,
  DropdownButton,
  MenuItem,
  Modal,
  Input,
  ListGroup,
  ListGroupItem,
  Glyphicon,
  OverlayTrigger,
  Tooltip
} from 'react-bootstrap';
import _ from 'lodash';

var EditorToolbar = React.createClass({
  getInitialState() {
    return {
      showCreateModal: false,
      showUploadModal: false,
    };
  },
  openUploadModal() {
    this.setState({showUploadModal: true});
  },
  closeUploadModal() {
    this.setState({showUploadModal: false});
  },
  onDrop(files) {
    var req = request.post('/api/editor/upload');
    req.attach('file', files[0], files[0].name);
    req.end(() => {
      EditorActionCreators.getCode(this.props.filename);
      this.closeUploadModal();
    });
  },
  openCreateModal() {
    this.setState({showCreateModal: true});
  },
  closeCreateModal() {
    this.setState({showCreateModal: false});
  },
  createFile() {
    var filename = this.refs.filenameInput.getValue();
    request
      .post('/api/editor/create')
      .send({filename: filename})
      .end((err, res) => {
        if (res.ok) {
          this.closeCreateModal();
          EditorActionCreators.setFilename(this.props.filename);
          EditorActionCreators.getCode(this.props.filename);
        } else {
          alert(res.text);
        }
      });
  },
  deleteFile() {
    if (confirm("This file will be deleted forever. Are you sure?")) {
      request.del('/api/editor/delete/' + this.props.filename).end(function(err) {
        if (err) {
          alert(err);
        } else {
          EditorActionCreators.setFilename('student_code.py');
          EditorActionCreators.getCode('student_code.py');
        }
      });
    }
  },
  render() {
    return (
      <div>
        <Modal
          show={this.state.showUploadModal}
          onHide={this.closeUploadModal}>
          <Modal.Header closeButton>
            <Modal.Title>Upload your code file.</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Dropzone
              style={{width:'100%', height:'300px', border:'2px dashed black'}}
              onDrop={this.onDrop}
              multiple={ false }>
              <div style={{padding: '10px 10px 10px 10px'}}>
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
            <Button onClick={this.closeUploadModal}>Close</Button>
          </Modal.Footer>
        </Modal>
        <Modal show={this.state.showCreateModal} onHide={this.closeCreateModal}>
          <Modal.Header closeButton>
            <div>Create New File</div>
          </Modal.Header>
          <Modal.Body>
            <Input
              ref="filenameInput"
              type="text"
              label="Enter a filename"
              placeholder="Type a filename here"
            />
          </Modal.Body>
          <Modal.Footer>
            <Button bsSize="small" bsStyle='default' onClick={this.createFile}>
              Create
            </Button>
          </Modal.Footer>
        </Modal>
        <ButtonToolbar id="editor-toolbar">
          <ButtonGroup id="choose-file-button">
            <OverlayTrigger
              placement="top"
              overlay={
                <Tooltip id="choose-file-tooltip">Choose file</Tooltip>}>
              <DropdownButton
                id="FileSelectorDropdown"
                bsSize="small"
                title={
                  this.props.filename + (this.props.unsavedChanges ? '*' : '')}
                onClick={EditorActionCreators.getFilenames}>
                {_.map(this.props.filenames, (fname)=>{
                  return (
                    <MenuItem key={fname} onClick={()=>{
                      this.props.changeFile(fname);
                    }}>
                      {fname}
                    </MenuItem>
                  );
                })}
              </DropdownButton>
            </OverlayTrigger>
          </ButtonGroup>
          <ButtonGroup id="file-operations-buttons">
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="save-tooltip">Save</Tooltip>}>
              <Button onClick={this.props.saveCode} bsSize="small">
                <Glyphicon glyph="floppy-disk" />
              </Button>
            </OverlayTrigger>
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="open-tooltip">Create</Tooltip>}>
              <Button onClick={this.openCreateModal} bsSize="small">
                <Glyphicon glyph="file" />
              </Button>
            </OverlayTrigger>
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="delete-tooltip">Delete</Tooltip>}>
              <Button onClick={this.deleteFile} bsSize="small">
                <Glyphicon glyph="trash" />
              </Button>
            </OverlayTrigger>
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="upload-tooltip">Upload</Tooltip>}>
              <Button onClick={this.openUploadModal} bsSize="small">
                <Glyphicon glyph="upload" />
              </Button>
            </OverlayTrigger>
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="download-tooltip">Download</Tooltip>}>
              <Button
                href={'/api/editor/download?filename=' + this.props.filename}
                bsSize="small">
                <Glyphicon glyph="download" />
              </Button>
            </OverlayTrigger>
          </ButtonGroup>
          <ButtonGroup id="code-execution-buttons">
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="run-tooltip">Run</Tooltip>}>
              <Button
                onClick={this.props.startRobot}
                bsSize="small"
                disabled={this.props.status || !this.props.connection}
                bsStyle="success">
                <Glyphicon glyph="play" />
              </Button>
            </OverlayTrigger>
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="stop-tooltip">Stop</Tooltip>}>
              <Button
                onClick={this.props.stopRobot}
                bsSize="small"
                disabled={!this.props.status || !this.props.connection}
                bsStyle="danger">
                <Glyphicon glyph="stop" />
              </Button>
            </OverlayTrigger>
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="toggle-tooltip">Toggle Console</Tooltip>}>
              <Button
                onClick={this.props.toggleConsole}
                bsSize="small">
                <Glyphicon glyph="console" />
              </Button>
            </OverlayTrigger>
            <OverlayTrigger
              placement="top"
              overlay={<Tooltip id="clear-tooltip">Clear Console</Tooltip>}>
              <Button
                onClick={this.props.clearConsole}
                bsSize="small">
                <Glyphicon glyph="remove" />
              </Button>
            </OverlayTrigger>
          </ButtonGroup>
        </ButtonToolbar>
      </div>
    );
  }
});

export default EditorToolbar;
