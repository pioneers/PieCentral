import React from 'react';
import { Link } from 'react-router-dom';
import { Alignment, Navbar } from '@blueprintjs/core';

import { ThemeToggleButton } from './util';

class Scoreboard extends React.Component {
  render() {
    return (
      <div>
        <nav>
          <Navbar>
            <Navbar.Group>
              <Navbar.Heading>Shepherd Scoreboard</Navbar.Heading>
              <Navbar.Divider />
              <Link to='/dashboard'>Dashboard</Link>
            </Navbar.Group>
            <Navbar.Group align={Alignment.RIGHT}>
              <ThemeToggleButton />
            </Navbar.Group>
          </Navbar>
        </nav>
      </div>
    );
  }
}

export default Scoreboard;
