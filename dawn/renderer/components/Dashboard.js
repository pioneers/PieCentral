import React from 'react';
import PropTypes from 'prop-types';
import { Grid, Row, Col } from 'react-bootstrap';
import PeripheralList from './PeripheralList';
import GamepadList from './GamepadList';
import EditorContainer from './EditorContainer';

const Dashboard = props => (
  <Grid fluid>
    <Row>
      <Col smPush={8} sm={4}>
        <PeripheralList
          connectionStatus={props.connectionStatus}
          runtimeStatus={props.runtimeStatus}
        />
        <GamepadList />
      </Col>
      <Col smPull={4} sm={8}>
        <EditorContainer
          runtimeStatus={props.runtimeStatus}
          isRunningCode={props.isRunningCode}
        />
      </Col>
    </Row>
  </Grid>
);

Dashboard.propTypes = {
  connectionStatus: PropTypes.bool,
  runtimeStatus: PropTypes.bool,
  isRunningCode: PropTypes.bool,
};

export default Dashboard;
