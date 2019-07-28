import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import {
  Alignment,
  Intent,
  Navbar,
  Spinner,
} from '@blueprintjs/core';

import { ThemeToggleButton } from './util';

class Scoreboard extends React.Component {
  constructor(props) {
    super(props);
    this.timerRef = React.createRef();
  }

  componentDidMount() {
    let [spinner] = document.getElementsByClassName('bp3-spinner-animation');
    let [svg] = (spinner || {}).children;
    if (svg) {
      svg.setAttribute('viewBox', '0 0 100 100');
      svg.setAttribute('stroke-width', 1.4);
    }
  }

  render() {
    let phaseProgress = 0;
    let { remainingDuration, totalDuration } = this.props;
    if (!isNaN(remainingDuration) && !isNaN(remainingDuration)) {
      phaseProgress = remainingDuration/totalDuration;
    }

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
        <main>
          <Spinner
            className='scoreboard-timer'
            value={phaseProgress}
            size={700}
            intent={phaseProgress > 0.05 ? Intent.PRIMARY : Intent.DANGER}
            ref={this.timerRef}
          />
        </main>
      </div>
    );
  }
}

export default connect(state => ({ ...state.match.phase }))(Scoreboard);
