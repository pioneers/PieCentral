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

console.log(Object.entries(ALLIANCES));

const TeamFormRow = props => (
  <Row className='team-form-row' gutterWidth={props.gutterWidth}>
    <Col md={3}>
      <NumericInput
        disabled={props.disabled}
        placeholder='Team number'
        buttonPosition='none'
        value={props.team.number}
        onValueChange={number => props.updateTeam(props.index, { number })}
        fill
      />
    </Col>
    <Col md={3}>
      <InputGroup
        disabled={props.disabled}
        placeholder='Team name'
        value={props.team.name || ''}
        onChange={event => props.updateTeam(props.index, { name: event.target.value })}
      />
    </Col>
    <Col md={3}>
      <InputGroup
        disabled={props.disabled}
        placeholder='Hostname'
        value={props.team.hostname || ''}
        onChange={event => props.updateTeam(props.index, { hostname: event.target.value })}
      />
    </Col>
    <Col md={2}>
      <HTMLSelect
        fill
        disabled={props.disabled}
        options={Object.entries(ALLIANCES).map(([value, label]) => ({value, label}))}
        value={props.team.alliance || 0}
        onChange={event => props.updateTeam(props.index, { alliance: event.target.value })}
      />
    </Col>
    <Col md={1}>
      <Button
        minimal
        icon='cross'
        disabled={props.disabled}
        intent={Intent.DANGER}
        onClick={() => props.removeTeam(props.index)}
      />
    </Col>
  </Row>
);

class TeamsCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = { teams: [{}] };
    this.addTeam = this.addTeam.bind(this);
    this.updateTeam = this.updateTeam.bind(this);
    this.removeTeam = this.removeTeam.bind(this);
  }

  addTeam() {
    this.setState({ teams: this.state.teams.concat([{}]) });
  }

  updateTeam(index, update) {
    let teams = this.state.teams;
    this.setState({
      teams: teams.slice(0, index).concat([
        Object.assign(teams[index], update)
      ]).concat(teams.slice(index + 1))
    });
  }

  removeTeam(index) {
    let teams = this.state.teams;
    this.setState({ teams: teams.slice(0, index).concat(teams.slice(index + 1)) });
  }

  render() {
    return (
      <Card>
        <H2>Teams</H2>
        <div className='team-form'>
          <Row gutterWidth={TeamsCard.GUTTER_WIDTH}>
            <Col><strong>Team number</strong></Col>
            <Col><strong>Team name</strong></Col>
            <Col><strong>Hostname</strong></Col>
            <Col><strong>Alliance</strong></Col>
          </Row>
          {this.state.teams.map((team, index) =>
            <TeamFormRow
              key={index}
              index={index}
              team={team}
              gutterWidth={TeamsCard.GUTTER_WIDTH}
              updateTeam={this.updateTeam}
              removeTeam={this.removeTeam}
            />
          )}
        </div>
        <ButtonGroup>
          <Button text='Add Team' onClick={this.addTeam} />
          <Button text='Populate' />
          <Button text='Update' />
        </ButtonGroup>
      </Card>
    );
  }
}

TeamsCard.GUTTER_WIDTH = 12;

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
          <TeamsCard />
        </Col>
        <Col md={4}>
          <MatchCard />
        </Col>
      </Row>
    );
  }
};

export default GamePanel;
