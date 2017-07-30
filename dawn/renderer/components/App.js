import React from 'react';
import Joyride from 'react-joyride';
import { remote, ipcRenderer } from 'electron';
import { connect } from 'react-redux';
import smalltalk from 'smalltalk';
import Dashboard from './Dashboard';
import DNav from './DNav';
import joyrideSteps from './JoyrideSteps';
import { removeAsyncAlert } from '../actions/AlertActions';
import { updateFieldControl } from '../actions/FieldActions';
import { ipChange } from '../actions/InfoActions';
import { logging, startLog } from '../utils/utils';

const storage = remote.require('electron-json-storage');

class AppComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      steps: [],
      tourRunning: false,
    };
    this.addSteps = this.addSteps.bind(this);
    this.addTooltip = this.addTooltip.bind(this);
    this.startTour = this.startTour.bind(this);
    this.joyrideCallback = this.joyrideCallback.bind(this);
    this.updateAlert = this.updateAlert.bind(this);
    startLog();
  }

  componentDidMount() {
    this.addSteps(joyrideSteps);
    ipcRenderer.on('start-interactive-tour', () => {
      this.startTour();
    });
    storage.has('firstTime', (hasErr, hasKey) => {
      if (hasErr) {
        logging.log(hasErr);
        return;
      }

      if (!hasKey) {
        this.startTour();
        storage.set('firstTime', { first: true }, (setErr) => {
          if (setErr) logging.log(setErr);
        });
      }
    });

    storage.get('fieldControl', (err, data) => {
      if (err) {
        logging.log(err);
        return;
      }
      this.props.onFCUpdate(data);
      ipcRenderer.send('LCM_CONFIG_CHANGE', data);
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

  shouldComponentUpdate(nextProps, nextState) {
    return nextProps !== this.props || nextState !== this.state;
  }

  addSteps(steps) {
    if (!Array.isArray(steps)) {
      steps = [steps];
    }
    if (steps.length === 0) {
      return;
    }
    this.setState((currentState) => {
      currentState.steps = currentState.steps.concat(steps);
      return currentState;
    });
  }

  addTooltip(data) {
    this.joyride.addTooltip(data);
  }

  startTour() {
    this.setState({ tourRunning: true });
  }

  joyrideCallback(action) {
    if (action.type === 'finished') {
      this.setState({ tourRunning: false });
      this.joyride.reset(false);
    }
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
        <DNav
          startTour={this.startTour}
          runtimeStatus={this.props.runtimeStatus}
          connection={this.props.connectionStatus}
          battery={this.props.batteryLevel}
          batterySafety={this.props.batterySafety}
          isRunningCode={this.props.isRunningCode}
          ipAddress={this.props.ipAddress}
          onIPChange={this.props.onIPChange}
          runtimeVersion={this.props.runtimeVersion}
        />
        <Joyride
          ref={(c) => { this.joyride = c; }}
          steps={this.state.steps}
          type="continuous"
          showSkipButton
          autoStart
          run={this.state.tourRunning}
          callback={this.joyrideCallback}
          locale={{
            back: 'Previous',
            close: 'Close',
            last: 'End Tour',
            next: 'Next',
            skip: 'Skip Tour',
          }}
        />
        <div style={{ height: '35px', marginBottom: '21px' }} />
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
  batterySafety: React.PropTypes.bool,
  isRunningCode: React.PropTypes.bool,
  asyncAlerts: React.PropTypes.array,
  onAlertDone: React.PropTypes.func,
  ipAddress: React.PropTypes.string,
  onIPChange: React.PropTypes.func,
  runtimeVersion: React.PropTypes.string,
  onFCUpdate: React.PropTypes.func,
};

const mapStateToProps = state => ({
  connectionStatus: state.info.connectionStatus,
  runtimeStatus: state.info.runtimeStatus,
  batteryLevel: state.peripherals.batteryLevel,
  batterySafety: state.peripherals.batterySafety,
  isRunningCode: state.info.isRunningCode,
  asyncAlerts: state.asyncAlerts,
  ipAddress: state.info.ipAddress,
  runtimeVersion: state.peripherals.runtimeVersion,
});

const mapDispatchToProps = dispatch => ({
  onAlertDone(id) {
    dispatch(removeAsyncAlert(id));
  },
  onIPChange: (ipAddress) => {
    dispatch(ipChange(ipAddress));
  },
  onFCUpdate: (ipAddress) => {
    dispatch(updateFieldControl(ipAddress));
  },
});

const App = connect(mapStateToProps, mapDispatchToProps)(AppComponent);

export default App;
