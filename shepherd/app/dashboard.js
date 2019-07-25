import React from 'react';
import { Alignment, Navbar, Tab, Tabs } from '@blueprintjs/core';

class GamePanel extends React.Component {
  render() {
    return (<span>Game</span>);
  }
}

class MetricsPanel extends React.Component {
  render() {
    return (<span>Metrics</span>);
  }
}

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.handleTabChange = this.handleTabChange.bind(this);
    this.state = { tabId: 'game' };
  }

  handleTabChange(tabId) {
    this.setState({ tabId });
  }

  render() {
    return (
      <Navbar>
        <Navbar.Group>
          <Navbar.Heading>Shepherd</Navbar.Heading>
          <Navbar.Divider />
          <Tabs
              id='navbar-tabs'
              className='navbar-tabs'
              selectedTabId={this.state.tabId}
              onChange={this.handleTabChange}
              large
          >
            <Tab id='game' title='Game' />
            <Tab id='metrics' title='Metrics' />
          </Tabs>
        </Navbar.Group>
      </Navbar>
    );
  }
}

export default Dashboard;
