import React from 'react';
import { Grid, Row, Col } from 'react-bootstrap';
import FinalCompPeripheralListContainer from './FinalCompPeripheralListContainer';
import GamepadsContainer from './GamepadsContainer';
import EditorContainer from './EditorContainer';

const Dashboard = (props) => (
  <Grid fluid>
    <Row>
      <Col smPush={8} sm={4}>
        <FinalCompPeripheralListContainer
          connectionStatus={props.connectionStatus}
          runtimeStatus={props.runtimeStatus}
        />
        <GamepadsContainer />
      </Col>
      <Col smPull={4} sm={8}>
        <EditorContainer
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
