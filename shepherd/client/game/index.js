import React from 'react';
import { Row, Col } from 'react-grid-system';

import TeamEditor from './team';
import PhaseEditor from './phase';
import MatchEditor from './match';

const GamePanelHelp = props => (
  <div>
    <h3>Team Editor</h3>
    <p>
      Use the team editor to configure match-specific team information.
      Ideally, team information can be populated directly from the match schedule.
    </p>
    <ul>
      <li>
        <strong>Team number</strong>: A unique positive integer associated with each team.
        Check PiE Drive for these numbers.
      </li>
      <li>
        <strong>Team name</strong>: The name that will be displayed on the scoreboard.
      </li>
      <li>
        <strong>Hostname</strong>: The hostname or raw IP address of that team's robot.
        A hostname may read like <code>team00.local</code>.
        An IP address may read like <code>192.168.128.200</code>.
      </li>
    </ul>
  </div>
);

class GamePanel extends React.Component {
  render() {
    let gutterWidth = this.props.gutterWidth || 16;
    return (
      <div>
        <Row gutterWidth={gutterWidth}>
          <Col xl={6} lg={12}>
            <TeamEditor />
          </Col>
          <Col xl={6} lg={12}>
            <MatchEditor />
          </Col>
        </Row>
        <Row gutterWidth={gutterWidth}>
          <Col>
            <PhaseEditor />
          </Col>
        </Row>
      </div>
    );
  }
};

export { GamePanel, GamePanelHelp };
