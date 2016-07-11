import React from 'react';
import Joyride from 'react-joyride';
import Dashboard from './Dashboard';
import joyrideSteps from './JoyrideSteps';
import smalltalk from 'smalltalk';
import { removeAsyncAlert } from '../actions/AlertActions';
import { remote, ipcRenderer } from 'electron';
import { connect } from 'react-redux';
const storage = remote.require('electron-json-storage');

class AppComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      steps: [],
    };
    this.addSteps = this.addSteps.bind(this);
    this.addTooltip = this.addTooltip.bind(this);
    this.startTour = this.startTour.bind(this);
    this.completeCallback = this.completeCallback.bind(this);
    this.updateAlert = this.updateAlert.bind(this);
  }

  componentDidMount() {
    this.addSteps(joyrideSteps);
    ipcRenderer.on('start-interactive-tour', () => {
      this.startTour();
    });
    storage.has('firstTime').then((hasKey) => {
      if (!hasKey) {
        this.startTour();
        storage.set('firstTime', { first: true }, (err) => {
          if (err) throw err;
        });
      }
    });
  }

  componentWillReceiveProps(nextProps) {
    const asyncAlerts = nextProps.asyncAlerts;
    // If the alerts list has changed, display the latest one.
    if (asyncAlerts !== this.props.asyncAlerts) {
      const latestAlert = asyncAlerts[asyncAlerts.length - 1];
      if (latestAlert !== undefined) {
        this.updateAlert(latestAlert);
      }
    }
  }

  addSteps(steps) {
    const joyride = this.refs.joyride;
    if (!Array.isArray(steps)) {
      steps = [steps];
    }
    if (!steps.length) {
      return false;
    }
    this.setState((currentState) => {
      currentState.steps = currentState.steps.concat(joyride.parseSteps(steps));
      return currentState;
    });
  }

  addTooltip(data) {
    this.refs.joyride.addTooltip(data);
  }

  startTour() {
    this.refs.joyride.start(true);
  }

  completeCallback() {
    this.refs.joyride.reset(false);
  }

  updateAlert(latestAlert) {
    smalltalk.alert(latestAlert.heading, latestAlert.message).then(() => {
      this.props.onAlertDone(latestAlert.id);
    }, () => {
      this.props.onAlertDone(latestAlert.id);
    });
  }

  render() {
    return (
      <div>
        <Joyride
          ref="joyride"
          steps={this.state.steps}
          type="continuous"
          completeCallback={this.completeCallback}
          locale={{
            back: 'Previous',
            close: 'Close',
            last: 'End Tour',
            next: 'Next',
            skip: 'Skip Tour',
          }}
        />
        <div style={{ height: '10px' }} />
        <Dashboard
          {...this.props}
          addSteps={this.addSteps}
          addTooltip={this.addTooltip}
          connectionStatus={this.props.connectionStatus}
          runtimeStatus={this.props.runtimeStatus}
          isRunningCode={this.props.isRunningCode}
        />
      </div>
    );
  }
}

AppComponent.propTypes = {
  connectionStatus: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  batteryLevel: React.PropTypes.number,
  isRunningCode: React.PropTypes.bool,
  asyncAlerts: React.PropTypes.array,
  onAlertDone: React.PropTypes.func,
};

const mapStateToProps = (state) => ({
  connectionStatus: state.info.connectionStatus,
  runtimeStatus: state.info.runtimeStatus,
  batteryLevel: state.info.batteryLevel,
  isRunningCode: state.info.isRunningCode,
  asyncAlerts: state.asyncAlerts,
});

const mapDispatchToProps = (dispatch) => ({
  onAlertDone(id) {
    dispatch(removeAsyncAlert(id));
  },
});

const App = connect(mapStateToProps, mapDispatchToProps)(AppComponent);

export default App;
