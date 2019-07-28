import React from 'react';
import { Row, Col } from 'react-grid-system';
import {
  Card,
  H2
} from '@blueprintjs/core';

class PhaseEditor extends React.Component {
  render() {
    return (
      <Card>
        <H2>Phases</H2>
        <Row>
          <Col><strong>Phase name</strong></Col>
        </Row>
      </Card>
    );
  }
}

export default PhaseEditor;
