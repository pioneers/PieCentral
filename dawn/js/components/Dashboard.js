import React from 'react';
import { Grid, Row, Col } from 'react-bootstrap';
import PeripheralList from './PeripheralList';
import FinalCompPeripheralList from './FinalCompPeripheralList';
import Peripheral from './Peripheral';
import Gamepads from './Gamepads';
import Editor from './Editor';

export default React.createClass({
  displayName: 'Dashboard',
  render() {
    return (
      <Grid fluid>
        <Row>
          <Col smPush={8} sm={4}>
            <FinalCompPeripheralList
	      connectionStatus={this.props.connectionStatus}
              runtimeStatus={this.props.runtimeStatus}/>
            <Gamepads />
          </Col>
          <Col smPull={4} sm={8}>
            <Editor
              consoleData={this.props.consoleData}
              runtimeStatus={this.props.runtimeStatus}
              isRunningCode={this.props.isRunningCode}/>
          </Col>
        </Row>
      </Grid>
    );
  }
});
