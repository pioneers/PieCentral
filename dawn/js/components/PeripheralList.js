/**
 * A generic component for displaying a list of Peripherals.
 */

import React from 'react';
import {Panel, ListGroup} from 'react-bootstrap';

var PeripheralList = React.createClass({
  getDefaultProps: function() {
    return {
      header: 'PeripheralList'
    };
  },
  render() {
    return (
      <Panel
        id="peripherals-panel"
        header={this.props.header}
        bsStyle="primary">
        <ListGroup fill style={{marginBottom: '5px'}}>
          {this.props.children}
        </ListGroup>
      </Panel>
    );
  }
});

export default PeripheralList;
