/**
 * A generic component for displaying a list of Peripherals.
 */

import React from 'react';
import { Panel, ListGroup } from 'react-bootstrap';

const PeripheralList = (props) => (
  <Panel
    id="peripherals-panel"
    header={props.header}
    bsStyle="primary"
  >
    <ListGroup fill style={{ marginBottom: '5px' }}>
      {props.children}
    </ListGroup>
  </Panel>
);

PeripheralList.defaultProps = {
  header: 'PeripheralList',
};

PeripheralList.propTypes = {
  header: React.PropTypes.string,
  children: React.PropTypes.any,
};

export default PeripheralList;
