import React from 'react';
import NameEdit from './NameEdit';
import numeral from 'numeral';
import _ from 'lodash';

var ColorSensor = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    peripheralType: React.PropTypes.string,
    id: React.PropTypes.string,
    value: React.PropTypes.array
  },
  /* Convert the separate R, G, B integer values to hex representation,
   * with the format '#RRGGBB'
   */
  getHexColorValue() {
    let hexRepresentation = _.map(_.slice(this.props.value, 0, 3), (val)=>{
      let hexVal = val.toString(16);
      return hexVal.length === 1 ? '0' + hexVal : hexVal;
    }).join('');
    return '#' + hexRepresentation;
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}>
          <NameEdit name={this.props.name} id={this.props.id} />
          <small> {this.props.peripheralType} </small>
        </h4>
        <div style={{
          float: 'right',
          width: '35px',
          height: '35px',
          backgroundColor: this.getHexColorValue()}}>
        </div>
      </div>
    </div>
    );
  }
});

export default ColorSensor;
