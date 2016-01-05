import React from 'react';
import Joyride from 'react-joyride';
import DNav from './DNav';
import Dashboard from './Dashboard';
import RobotInfoStore from '../stores/RobotInfoStore';
import joyrideSteps from './JoyrideSteps';

export default React.createClass({
  displayName: 'Dawn',
  getInitialState() {
    return {
      steps: [],
      consoleData: [],
      isRunningCode: false,
      connectionStatus: true,
      batteryLevel: 0
    };
  },
  componentDidMount() {
    this.addSteps(joyrideSteps);
    RobotInfoStore.on('change', this.updateRobotInfo);
  },
  componentWillUnmount() {
    RobotInfoStore.removeListener('change', this.updateRobotInfo);
  },
  updateRobotInfo() {
    this.setState({
      consoleData: RobotInfoStore.getConsoleData(),
      isRunningCode: RobotInfoStore.getIsRunningCode(),
      connectionStatus: RobotInfoStore.getConnectionStatus(),
      batteryLevel: RobotInfoStore.getBatteryLevel()
    });
  },
  addSteps(steps) {
    let joyride = this.refs.joyride;
    if (!Array.isArray(steps)) {
      steps = [ steps ];
    }
    if (!steps.length) {
      return false;
    }
    this.setState((currentState) => {
      currentState.steps = currentState.steps.concat(joyride.parseSteps(steps));
      return currentState;
    });
  },
  addTooltip(data) {
    this.refs.joyride.addTooltip(data);
  },
  startTour() {
    this.refs.joyride.start(true);
  },
  completeCallback(steps, skipped) {
    this.refs.joyride.reset(false);
  },
  render() {
    return (
      <div>
        <DNav {...this.props}
          startTour={this.startTour}
          connection={this.state.connectionStatus}
          battery={this.state.batteryLevel}
        />
        <Joyride
          ref="joyride"
          steps={this.state.steps}
          type="continuous"
          showSkipButton={true}
          completeCallback={this.completeCallback}
        />
        <div style={{ height: '60px', marginBottom: '21px' }}/>
        <Dashboard {...this.props}
          addSteps={this.addSteps}
          addTooltip={this.addTooltip}
          consoleData={this.state.consoleData}
          batteryLevel={this.state.batteryLevel}
          connectionStatus={this.state.connectionStatus}
          isRunningCode={this.state.isRunningCode}
        />
      </div>
    );
  }
});
