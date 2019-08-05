import React from 'react';
import { Row, Col } from 'react-grid-system';
import {
  Card,
} from '@blueprintjs/core';

import TeamEditor from './team';
import MatchEditor from './match';
import ResourceStatusTable from './resource';

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
            <Card>
              <TeamEditor />
              <MatchEditor />
            </Card>
          </Col>
          <Col xl={6} lg={12}>
            <Card>
              <ResourceStatusTable />
            </Card>
          </Col>
        </Row>
      </div>
    );
  }
};

export { GamePanel, GamePanelHelp };
