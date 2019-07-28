import React from 'react';
import { Row, Col } from 'react-grid-system';
import {
  Alert,
  Button,
  ButtonGroup,
  Card,
  ControlGroup,
  H2,
  HTMLSelect,
  InputGroup,
  Intent,
  NumericInput
} from '@blueprintjs/core';
import { ALLIANCES } from './util';
import TeamEditor from './team';

class MatchCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      startLoading: false,
      eStopConfirm: false,
      eStopLoading: false,
    };

    this.start = this.start.bind(this);
    this.eStop = this.eStop.bind(this);
  }

  start() {
    this.setState({ startLoading: true });
  }

  eStop() {
    this.setState({ eStopConfirm: false, eStopLoading: true }, () => {
      console.log('TODO: issuing E-stop');
    });
  }

  render() {
    return (
      <Card>
        <H2>Match</H2>
        <NumericInput placeholder='Match number' />
        <ButtonGroup>
          <Button
            text='Start'
            intent='primary'
            icon='play'
            onClick={this.start}
            loading={this.state.startLoading}
          />
          <Button
            text='E-Stop'
            intent={Intent.DANGER}
            icon='flame'
            onClick={() => this.setState({ eStopConfirm: true })}
            loading={this.state.eStopLoading}
          />
          <Alert
            cancelButtonText='Cancel'
            confirmButtonText='Confirm'
            icon='flame'
            intent={Intent.DANGER}
            isOpen={this.state.eStopConfirm}
            onCancel={() => this.setState({ eStopConfirm: false })}
            onConfirm={this.eStop}
          >
            <p>
              Are you sure you want to issue an emergency stop to <strong>all</strong> robots?
              The match will be cancelled.
            </p>
          </Alert>
        </ButtonGroup>
      </Card>
    );
  }
}

class GamePanel extends React.Component {
  render() {
    return (
      <Row>
        <Col md={8}>
          <TeamEditor />
        </Col>
        <Col md={4}>
          <MatchCard />
        </Col>
      </Row>
    );
  }
};

export default GamePanel;
