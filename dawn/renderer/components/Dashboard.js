import React from 'react';
import { Grid, Row, Col } from 'react-bootstrap';
import FinalCompPeripheralList from './FinalCompPeripheralList';
import Gamepads from './Gamepads';
import Editor from './Editor';

const Dashboard = (props) => (
  <Grid fluid>
    <Row>
      <Col smPush={8} sm={4}>
        <FinalCompPeripheralList
          connectionStatus={props.connectionStatus}
          runtimeStatus={props.runtimeStatus}
        />
        <Gamepads />
      </Col>
      <Col smPull={4} sm={8}>
        <Editor
          consoleData={props.consoleData}
          runtimeStatus={props.runtimeStatus}
          isRunningCode={props.isRunningCode}
        />
      </Col>
    </Row>
  </Grid>
);

Dashboard.propTypes = {
  connectionStatus: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  isRunningCode: React.PropTypes.bool,
  consoleData: React.PropTypes.array,
};

export default Dashboard;
