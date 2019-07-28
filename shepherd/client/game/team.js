import React from 'react';
import { Row, Col } from 'react-grid-system';
import { connect } from 'react-redux';
import {
  Button,
  ButtonGroup,
  Card,
  H2,
  HTMLSelect,
  InputGroup,
  Intent,
  NumericInput
} from '@blueprintjs/core';
import { ALLIANCES, toOptions } from '../util';

const ADD_TEAM = 'ADD_TEAM';
const UPDATE_TEAM = 'UPDATE_TEAM';
const DELETE_TEAM = 'DELETE_TEAM';

const addTeam = () => ({ type: ADD_TEAM });
const updateTeam = (index, update = {}) => ({ type: UPDATE_TEAM, index, update });
const deleteTeam = index => ({ type: DELETE_TEAM, index });

export function handleTeamsUpdate(teams = [{}], { type, index, update }) {
  if (type === ADD_TEAM) {
    return [...teams, {}];
  }
  let before = teams.slice(0, index);
  let after = teams.slice(index + 1);
  switch(type) {
    case UPDATE_TEAM:
      let updatedTeam = Object.assign({}, teams[index], update);
      return before.concat([updatedTeam]).concat(after);
    case DELETE_TEAM: return before.concat(after);
    default: return teams;
  }
}

const TeamFormRow = props => (
  <Row className='team-form-row' gutterWidth={props.gutterWidth}>
    <Col md={3}>
      <NumericInput
        disabled={props.disabled}
        placeholder='Team number'
        buttonPosition='none'
        value={props.team.number}
        onValueChange={number => props.updateTeam({ number })}
        fill
      />
    </Col>
    <Col md={3}>
      <InputGroup
        disabled={props.disabled}
        placeholder='Team name'
        value={props.team.name || ''}
        onChange={event => props.updateTeam({ name: event.target.value })}
      />
    </Col>
    <Col md={3}>
      <InputGroup
        disabled={props.disabled}
        placeholder='Hostname'
        value={props.team.hostname || ''}
        onChange={event => props.updateTeam({ hostname: event.target.value })}
      />
    </Col>
    <Col md={2}>
      <HTMLSelect
        fill
        disabled={props.disabled}
        options={toOptions(ALLIANCES)}
        value={props.team.alliance || 0}
        onChange={event => props.updateTeam({ alliance: event.target.value })}
      />
    </Col>
    <Col md={1}>
      <Button
        minimal
        icon='cross'
        disabled={props.disabled}
        intent={Intent.DANGER}
        onClick={props.deleteTeam}
      />
    </Col>
  </Row>
);

class TeamEditor extends React.Component {
  render() {
    let gutterWidth = this.props.gutterWidth || 12;
    return (
      <Card>
        <H2>Teams</H2>
        <div className='team-form'>
          <Row gutterWidth={gutterWidth}>
            <Col><strong>Team number</strong></Col>
            <Col><strong>Team name</strong></Col>
            <Col><strong>Hostname</strong></Col>
            <Col><strong>Alliance</strong></Col>
          </Row>
          {this.props.teams.map((team, index) =>
            <TeamFormRow
              key={index}
              team={team}
              gutterWidth={gutterWidth}
              updateTeam={update => this.props.updateTeam(index, update)}
              deleteTeam={() => this.props.deleteTeam(index)}
            />
          )}
        </div>
        <ButtonGroup>
          <Button text='Add Team' onClick={this.props.addTeam} />
          <Button text='Populate From Schedule' />
          <Button text='Update Schedule' />
        </ButtonGroup>
      </Card>
    );
  }
}

export default connect(
  state => ({ teams: state.teams }),
  { addTeam, updateTeam, deleteTeam }
)(TeamEditor);
