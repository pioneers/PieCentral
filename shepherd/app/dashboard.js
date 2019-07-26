import React from 'react';
import { Alignment, Button, H1, Navbar, Tab, Tabs } from '@blueprintjs/core';

import GamePanel from './game';
import { DARK_THEME } from './util';


class MetricsPanel extends React.Component {
  render() {
    return (<span>Metrics</span>);
  }
}

class Dashboard extends React.Component {
  constructor(props) {
    super(props);

    this.panels = [{
      id: 'game',
      title: 'Game',
      component: <GamePanel />,
    }, {
      id: 'metrics',
      title: 'Metrics',
      component: <MetricsPanel />,
    }];
    this.state = { panelId: 'game' };

    this.handleTabChange = this.handleTabChange.bind(this);
    this.getPanel = this.getPanel.bind(this);
  }

  handleTabChange(panelId) {
    this.setState({ panelId });
  }

  getPanel() {
    return this.panels.find(panel => panel.id === this.state.panelId) || {};
  }

  render() {
    let { title, component } = this.getPanel();
    let themeToggleText, themeToggleIcon;
    if (this.props.theme === DARK_THEME) {
      themeToggleText = 'Light theme';
      themeToggleIcon = 'flash';
    } else {
      themeToggleText = 'Dark theme';
      themeToggleIcon = 'moon';
    }
    return (
      <div>
        <nav>
          <Navbar>
            <Navbar.Group>
              <Navbar.Heading>Shepherd Dashboard</Navbar.Heading>
              <Navbar.Divider />
              <Tabs
                  id='navbar-tabs'
                  className='navbar-tabs'
                  selectedTabId={this.state.panelId}
                  onChange={this.handleTabChange}
                  large
              >
                {this.panels.map(({ id, title }, index) =>
                  <Tab key={index} id={id} title={title} />)}
              </Tabs>
            </Navbar.Group>
            <Navbar.Group align={Alignment.RIGHT}>
              <Button
                text={themeToggleText}
                icon={themeToggleIcon}
                onClick={this.props.toggleTheme}
              />
            </Navbar.Group>
          </Navbar>
        </nav>
        <main>
          <H1>{title || 'Page Not Found'}</H1>
          {component || <p>No content available.</p>}
        </main>
      </div>
    );
  }
}

export default Dashboard;
