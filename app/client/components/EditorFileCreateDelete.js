import React from 'react';
import EditorActionCreators from '../actions/EditorActionCreators';
import request from 'superagent';
import {
  Modal,
  Button,
  ButtonGroup,
  Input
} from 'react-bootstrap';

var EditorFileCreate = React.createClass({
  getInitialState() {
    return {showModal: false};
  },
  openModal() {
    this.setState({showModal: true});
  },
  closeModal() {
    this.setState({showModal: false});
  },
  createFile() {
    var filename = this.refs.filenameInput.getValue();
    request
      .post('/api/editor/create')
      .send({filename: filename})
      .end((err, res) => {
        if (res.ok) {
          this.closeModal();
          EditorActionCreators.setFilename(filename);
          EditorActionCreators.getCode(filename);
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
        <ButtonGroup>
          <Button bsSize="small" bsStyle='default' onClick={this.openModal}>
            Create
          </Button>
          <Modal show={this.state.showModal} onHide={this.closeModal}>
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
          <Button bsSize="small" bsStyle='default' onClick={this.deleteFile}>
            Delete
          </Button>
        </ButtonGroup>
    );
  }
});

export default EditorFileCreate;
