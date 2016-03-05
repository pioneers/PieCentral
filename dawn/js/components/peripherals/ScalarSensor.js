/**
 * A component representing a scalar sensors (Line Follower, Potentiometer, Encoder)
 * Props:
 *   id: a unique id string
 *   value: the speed, from 0 to 100.
 */

import React from 'react';
import {ProgressBar} from 'react-bootstrap';
import NameEdit from './NameEdit';
import numeral from 'numeral';

var Motor = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    peripheralType: React.PropTypes.string,
    id: React.PropTypes.string,
    value: React.PropTypes.number
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}><NameEdit name={this.props.name} id={this.props.id} /><small> {this.props.peripheralType} </small></h4>
        <h4 style={{float: 'right'}}> {numeral(this.props.value).format('0.00')} </h4>
      </div>
      <ProgressBar now={this.props.value}></ProgressBar>
    </div>
    );
  }
});

export default Motor;
