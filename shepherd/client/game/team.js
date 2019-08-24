import React from 'react';
import { createActions, handleActions } from 'redux-actions';
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

export const { addTeam, updateTeam, deleteTeam } = createActions({
  ADD_TEAM: () => ({}),
  UPDATE_TEAM: (index, update = {}) => ({ index, update }),
  DELETE_TEAM: index => ({ index }),
});

export const handleTeamsUpdate = handleActions({
  ADD_TEAM: teams => [...teams, {}],
  UPDATE_TEAM: (teams, { payload: { index, update } }) => {
    let before = teams.slice(0, index);
    let after = teams.slice(index + 1);
    return [...before, {...teams[index], ...update}, ...after];
  },
  DELETE_TEAM: (teams, { payload: { index } }) =>
    teams.length > 1 ? [...teams.slice(0, index), ...teams.slice(index + 1)] : [{}],
}, [{}]);

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
        placeholder='Host'
        value={props.team.host || ''}
        onChange={event => props.updateTeam({ host: event.target.value })}
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
      <div className='game-form-section'>
        <H2>Teams</H2>
        <div>
          <Row gutterWidth={gutterWidth}>
            <Col><strong>Team number</strong></Col>
            <Col><strong>Team name</strong></Col>
            <Col><strong>Host</strong></Col>
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
        <Button text='Add Team' onClick={this.props.addTeam} />
      </div>
    );
  }
}

export default connect(
  state => ({ teams: state.teams }),
  { addTeam, updateTeam, deleteTeam }
)(TeamEditor);
