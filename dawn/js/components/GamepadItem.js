import React from 'react';
import {
  Panel,
  Modal,
  Button,
  ListGroupItem,
  Table,
  Grid,
  Row,
  Col
} from 'react-bootstrap';
import _ from 'lodash';
import numeral from 'numeral';

export default React.createClass({
  displayName: 'GamepadItem',
  propTypes: {
    gamepad: React.PropTypes.object,
    index: React.PropTypes.number
  },
  roundedValues() {
    return {
      axes: _.map(this.props.gamepad.axes, (axis) => numeral(axis).format('0.00000')),
      buttons: _.map(this.props.gamepad.buttons, (button) => numeral(button.value).format('0'))
    };
  },
  renderHeader() {
    return (
      <div>
        <h4 style={{display: 'inline'}}> Gamepad {this.props.index} </h4>
      </div>
    );
  },
  getInitialState() {
    return { showModal: false };
  },
  closeModal() {
    this.setState({ showModal: false });
  },
  openModal() {
    this.setState({ showModal: true })
  },
  render() {
    if (!this.props.gamepad) {
      return (<div/>);
    }
    let values = this.roundedValues();
    return (
      <ListGroupItem>
        <div style={{overflow: 'auto', width: '100%'}}>
          <span style={{float: 'left'}}>{this.renderHeader()}</span>
          <Button bsSize="small" onClick={this.openModal} style={{float: 'right'}}>Details</Button>
        </div>
        <Modal show={this.state.showModal} onHide={this.closeModal}>
          <Modal.Header closeButton>
            <Modal.Title>{this.renderHeader()}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <img src={'graphics/gamepad.png'} style={{width: '100%'}}/>
              <Table bordered>
                <tbody>
                  <tr>
                    <th>Button</th>
                    <td>0</td>
                    <td>1</td>
                    <td>2</td>
                    <td>3</td>
                    <td>4</td>
                    <td>5</td>
                    <td>6</td>
                    <td>7</td>
                    <td>8</td>
                    <td>9</td>
                    <td>10</td>
                    <td>11</td>
                    <td>12</td>
                    <td>13</td>
                    <td>14</td>
                    <td>15</td>
                  </tr>
                  <tr>
                    <th>Value</th>
                    <td>{values.buttons[0]}</td>
                    <td>{values.buttons[1]}</td>
                    <td>{values.buttons[2]}</td>
                    <td>{values.buttons[3]}</td>
                    <td>{values.buttons[4]}</td>
                    <td>{values.buttons[5]}</td>
                    <td>{values.buttons[6]}</td>
                    <td>{values.buttons[7]}</td>
                    <td>{values.buttons[8]}</td>
                    <td>{values.buttons[9]}</td>
                    <td>{values.buttons[10]}</td>
                    <td>{values.buttons[11]}</td>
                    <td>{values.buttons[12]}</td>
                    <td>{values.buttons[13]}</td>
                    <td>{values.buttons[14]}</td>
                    <td>{values.buttons[15]}</td>
                  </tr>
                </tbody>
              </Table>
              <Table bordered>
                <tbody>
                  <tr>
                    <th>Axis</th>
                    <td>0</td>
                    <td>1</td>
                    <td>2</td>
                    <td>3</td>
                  </tr>
                  <tr>
                    <th>Value</th>
                    <td>{values.axes[0]}</td>
                    <td>{values.axes[1]}</td>
                    <td>{values.axes[2]}</td>
                    <td>{values.axes[3]}</td>
                  </tr>
                </tbody>
              </Table>
          </Modal.Body>
        </Modal>
      </ListGroupItem>
    );
  }
});
