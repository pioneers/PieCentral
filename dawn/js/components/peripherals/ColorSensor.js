import React from 'react';
import NameEdit from './NameEdit';
import numeral from 'numeral';

var ColorSensor = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    peripheralType: React.PropTypes.string,
    id: React.PropTypes.string,
    value: React.PropTypes.array
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}><NameEdit name={this.props.name} id={this.props.id} /><small> {this.props.peripheralType} </small></h4>
        <h4 style={{float: 'right'}}> [{this.props.value[0]}, {this.props.value[1]}, {this.props.value[2]}]  </h4>
      </div>
    </div>
    );
  }
});

export default ColorSensor;
