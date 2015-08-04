import React from 'react';

export default React.createClass({
  render() {
    return <h3> Peripheral Not Found <small>{this.props.peripheralType}</small></h3>;
  }
});
