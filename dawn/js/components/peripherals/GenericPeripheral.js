/**
 * A generic peripheral, used when the peripheralType is unknown.
 */
import React from 'react';
import NameEdit from './NameEdit';

export default React.createClass({
  getDefaultProps() {
    return {
      peripheralType: 'peripheralType was undefined'
    };
  },
  render() {
    return (
      <div style={{overflow: 'auto'}}>
        <div style={{overflow: 'auto', width: '100%'}}>
          <h4 style={{float: 'left'}}>
            <NameEdit name={this.props.name} id={this.props.id} />
            <small>{this.props.peripheralType}</small>
          </h4>
          <h4 style={{float: 'right'}}>
            { this.props.value }
          </h4>
        </div>
      </div>
    );
  }
});
