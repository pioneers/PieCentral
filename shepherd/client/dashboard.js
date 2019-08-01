import React from 'react';
import { Link } from 'react-router-dom';
import { Container } from 'react-grid-system';
import {
  Alignment,
  Button,
  ButtonGroup,
  Classes,
  Drawer,
  H1,
  Navbar,
  Tab,
  Tabs
} from '@blueprintjs/core';

import { GamePanel, GamePanelHelp } from './game';
import ScheduleViewer from './schedule';
import { ThemeToggleButton } from './util';


class MetricsPanel extends React.Component {
  render() {
    return (<span>Metrics</span>);
  }
}

const DashboardHelp = props => {
  return (
    <Drawer isOpen={props.isOpen} onClose={props.onClose} title='Using the Shepherd Dashboard' icon='help'>
      <div className={Classes.DRAWER_BODY}>
        <div className={Classes.DIALOG_BODY}>
          {props.help}
        </div>
      </div>
    </Drawer>
  );
};

class Dashboard extends React.Component {
  constructor(props) {
    super(props);

    this.panels = [{
      id: 'game',
      title: 'Game',
      component: <GamePanel />,
      help: <GamePanelHelp />,
    }, {
      id: 'schedule',
      title: 'Schedule',
      component: <ScheduleViewer />,
    }, {
      id: 'metrics',
      title: 'Metrics',
      component: <MetricsPanel />,
    }];
    this.state = { panelId: 'game', isHelpOpen: false };

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
    let { title, component, help } = this.getPanel();
    return (
      <Container fluid style={{ maxWidth: 1600, paddingTop: 15, paddingBottom: 15 }}>
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
              <Navbar.Divider />
              <Link to='/scoreboard'>Scoreboard</Link>
            </Navbar.Group>
            <Navbar.Group align={Alignment.RIGHT}>
              <ButtonGroup>
                <Button
                  icon='help'
                  text='Help'
                  onClick={() => this.setState({ isHelpOpen: true })}
                />
                <ThemeToggleButton />
              </ButtonGroup>
            </Navbar.Group>
          </Navbar>
        </nav>
        <main>
          <H1>{title || 'Page Not Found'}</H1>
          {component || <p>No content available.</p>}
          <DashboardHelp
            isOpen={this.state.isHelpOpen}
            help={help || <p>No help page available.</p>}
            onClose={() => this.setState({ isHelpOpen: false })}
          />
        </main>
      </Container>
    );
  }
}

export default Dashboard;
