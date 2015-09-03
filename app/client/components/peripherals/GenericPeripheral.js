/**
 * A generic peripheral, used when the peripheralType is unknown.
 */
import React from 'react';

export default React.createClass({
  getDefaultProps() {
    return {
      peripheralType: 'peripheralType was undefined'
    };
  },
  render() {
    return <h4> Peripheral Type Unknown <small>{this.props.peripheralType}</small></h4>;
  }
});
