/**
 * A generic component for displaying a list of Peripherals.
 */

import React from 'react';
import {Panel} from 'react-bootstrap';

var PeripheralList = React.createClass({
  getDefaultProps: function() {
    return {
      header: 'PeripheralList'
    };
  },
  render() {
    return (
      <Panel header={this.props.header} bsStyle='primary'>
        {this.props.children}
      </Panel>
    );
  }
});

export default PeripheralList;
