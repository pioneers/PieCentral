import React from 'react';
import { Row, Col } from 'react-grid-system';
import { connect } from 'react-redux';
import {
  Alert,
  Button,
  ButtonGroup,
  Card,
  ControlGroup,
  FormGroup,
  H2,
  HTMLSelect,
  InputGroup,
  Intent,
  NumericInput
} from '@blueprintjs/core';
import { MODES, toOptions } from '../util';

const DEFAULT_MATCH = {
  phase: { totalDuration: NaN, remainingDuration: NaN }
};

const UPDATE_TIMER = 'UPDATE_TIMER';
const RESET_TIMER = 'RESET_TIMER';

export const updateTimer = update => ({ type: UPDATE_TIMER, update });

export function handleMatchUpdate(match = DEFAULT_MATCH, { type, update }) {
  switch (type) {
    case UPDATE_TIMER:
      return { ...match, phase: Object.assign({}, match.phase, update) };
    default:
      return match;
  }
}

class MatchEditor extends React.Component {
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
      <div>
        <H2>Match</H2>
        <Row>
          <Col>
            <FormGroup
              label='Match number'
              labelInfo='(optional)'
              helperText={
                <p>
                  The match number is used
                </p>
              }
            >
              <NumericInput placeholder='Match number' />
            </FormGroup>
          </Col>
          <Col>
            <FormGroup
              label='Match name'
              labelInfo='(optional)'
              helperText={
                <p>
                  This name will be shown on the scoreboard.
                  For example: <em>Semifinal Match 1 of 3</em>.
                </p>
              }
            >
              <InputGroup
                placeholder='Match name'
              />
            </FormGroup>
          </Col>
        </Row>
        <Row style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>
          <Col>
            <ButtonGroup>
              <Button
                text='Update'
              />
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
          </Col>
          <Col>
            <ControlGroup>
              <HTMLSelect options={toOptions(MODES)} />
              <Button text='Set mode' intent={Intent.WARNING} />
            </ControlGroup>
          </Col>
        </Row>
      </div>
    );
  }
}

export default connect()(MatchEditor);
