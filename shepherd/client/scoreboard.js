import React from 'react';
import { Row, Col } from 'react-grid-system';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { Container } from 'react-grid-system';
import {
  Alignment,
  Colors,
  Intent,
  Navbar,
  Spinner,
} from '@blueprintjs/core';
import { DARK_THEME, MODES } from './util';
import SVG from 'svg.js';

import { ThemeToggleButton } from './util';

class Scoreboard extends React.Component {
  constructor(props) {
    super(props);
    this.svgId = 'scoreboard-timer-canvas';
    this.timerRef = React.createRef();
  }

  componentDidMount() {
    let [spinner] = document.getElementsByClassName('bp3-spinner-animation');
    let [svg] = (spinner || {}).children;
    if (svg) {
      svg.setAttribute('viewBox', '0 0 100 100');
      svg.setAttribute('stroke-width', 2);
      svg.setAttribute('id', this.svgId);
      this.element = SVG.get(this.svgId);
      this.timerLabel = this.element.text('');
    }
  }

  render() {
    let phaseProgress = 0;
    let { remainingDuration, totalDuration } = this.props;
    if (!isNaN(remainingDuration) && !isNaN(remainingDuration)) {
      phaseProgress = remainingDuration/totalDuration;
    }

    if (this.timerLabel) {
      this.timerLabel
        .text(`${(remainingDuration/1000).toFixed(1)}s`)
        .center(50, 50);
    }

    let mode = MODES[this.props.mode] || '(Unknown mode)';
    let goldStyle = { color: this.props.theme == DARK_THEME ? Colors.GOLD4 : Colors.GOLD1 };
    let blueStyle = { color: Colors.BLUE3 };

    return (
      <Container fluid style={{ maxWidth: 1400, paddingTop: 15, paddingBottom: 15 }}>
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
        <main id="scoreboard">
          <Row>
            <Col style={goldStyle}>
              <h2>Gold Alliance</h2>
              <h3>De Anza</h3>
            </Col>
            <Col>
              <Spinner
                className='scoreboard-timer'
                value={phaseProgress}
                size={500}
                intent={phaseProgress > 0.1 ? Intent.PRIMARY : Intent.DANGER}
                ref={this.timerRef}
              />
              <h1>{mode} {!isNaN(totalDuration) &&
                <span>({(totalDuration/1000).toFixed(1)}s)</span>}
              </h1>
            </Col>
            <Col style={blueStyle}>
              <h2>Blue Alliance</h2>
              <h3>Albany</h3>
            </Col>
          </Row>
        </main>
      </Container>
    );
  }
}

export default connect(state => ({
  ...state.match.phase,
  theme: state.theme
}))(Scoreboard);
