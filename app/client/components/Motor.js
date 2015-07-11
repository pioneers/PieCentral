import React from 'react';
import {Panel, ProgressBar} from 'react-bootstrap';

var Motor = React.createClass({
  propTypes: {
    id: React.PropTypes.string,
    speed: React.PropTypes.number
  },
  render() {
    return <Panel header={this.props.id}>
      <h3>{this.props.speed}</h3>
      <ProgressBar now={this.props.speed}></ProgressBar>
    </Panel>;
  }
});

export default Motor;
