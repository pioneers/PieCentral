import React from 'react';

import { Card, H2 } from '@blueprintjs/core';

class AlliancesCard extends React.Component {
  render() {
    return (
      <Card>
        <H2>Alliances</H2>
      </Card>
    );
  }
}

class MatchCard extends React.Component {
  render() {
    return (
      <Card>
        <H2>Match</H2>
      </Card>
    );
  }
}

class GamePanel extends React.Component {
  render() {
    return (
      <div>
        <AlliancesCard />
        <MatchCard />
      </div>
    );
  }
};

export default GamePanel;
