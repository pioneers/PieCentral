import React from 'react';
import {
  Panel,
  Accordion,
  Button,
  ButtonGroup,
  ButtonToolbar
} from 'react-bootstrap';
import _ from 'lodash';
import RemoteRobotStore from '../stores/RemoteRobotStore';
import RobotActions from '../actions/RobotActions';

var ConsoleOutput = React.createClass({
  getInitialState() {
    return {output: []}
  },
  updateConsole() {
    this.setState({output: RemoteRobotStore.getConsoleData()});
  },
  componentDidMount() {
    RemoteRobotStore.on('change', this.updateConsole);
  },
  clearConsole() {
    RobotActions.clearConsole();
  },
  render() {
    return (
      <div>
        <ButtonToolbar>
          <ButtonGroup>
            <Button
              bsSize="small"
              bsStyle='default'
              onClick={ ()=> this.setState({ open: !this.state.open })}>
              Click to Show Output
            </Button>
          </ButtonGroup>
          <ButtonGroup>
            <Button
              bsSize="small"
              bsStyle='default'
              onClick={this.clearConsole}>
              Clear
            </Button>
          </ButtonGroup>
        </ButtonToolbar>
        <Panel collapsible expanded={this.state.open}>
          <pre style={{position: 'relative', height: '300px'}}>
            <div style={{
                position: 'absolute',
                bottom: '0',
                maxHeight: '300px',
                overflowY: 'auto',
                padding: '5px',
                width: '99%'
            }}>
            {_.map(this.state.output, (line, index)=>{
              return (<code key={index}>{line}</code>);
            })}
            </div>
          </pre>
        </Panel>
      </div>
    );
  }
});

export default ConsoleOutput;
