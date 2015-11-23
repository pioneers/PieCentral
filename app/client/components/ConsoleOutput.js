import React from 'react';
import { Panel, Accordion } from 'react-bootstrap';
import RemoteRobotStore from '../stores/RemoteRobotStore';

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
  render() {
    return (
      <Accordion>
        <Panel
          header="Click to Show Console Output"
          eventKey="1">
          <div style={{maxHeight: '300px', overflowY: 'auto'}}>
          { this.state.output.map((line, index)=><pre><code>{line}</code></pre>) }
          </div>
        </Panel>
      </Accordion>
    );
  }
});

export default ConsoleOutput;
