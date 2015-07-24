import React from 'react';
import {Label, ProgressBar} from 'react-bootstrap';

var Motor = React.createClass({
  propTypes: {
    id: React.PropTypes.string,
    speed: React.PropTypes.number
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}>Motor <small>{this.props.id}</small></h4>
        <h4 style={{float: 'right'}}>
        {
          this.props.disconnected
          ? <Label bsStyle='danger'>Disconnected</Label>
          : this.props.speed
        }
        </h4>
      </div>
      <ProgressBar now={this.props.speed}></ProgressBar>
    </div>
    );
  }
});

export default Motor;
