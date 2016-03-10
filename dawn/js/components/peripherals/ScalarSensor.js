import React from 'react';
import NameEdit from './NameEdit';
import numeral from 'numeral';

var ScalarSensor = React.createClass({
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
    </div>
    );
  }
});

export default ScalarSensor;
