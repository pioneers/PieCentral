import React from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import {
  Navbar,
  ButtonToolbar,
  ButtonGroup,
  Label,
} from 'react-bootstrap';
import ConfigBox from './ConfigBox';
import UpdateBox from './UpdateBox';
import StatusLabel from './StatusLabel';
import TooltipButton from './TooltipButton';
import { VERSION } from '../constants/Constants';
import { runtimeState } from '../utils/utils';

class DNavComponent extends React.Component {
  constructor(props) {
    super(props);
    this.toggleUpdateModal = this.toggleUpdateModal.bind(this);
    this.toggleConfigModal = this.toggleConfigModal.bind(this);
    this.state = {
      showUpdateModal: false,
      showConfigModal: false,
    };
  }

  toggleUpdateModal() {
    this.setState({ showUpdateModal: !this.state.showUpdateModal });
  }

  toggleConfigModal() {
    this.setState({ showConfigModal: !this.state.showConfigModal });
  }

  createHeader() {
    if (this.props.fieldControlStatus) {
      return `Dawn FC v${VERSION} ${(this.props.heart) ? '+' : '-'}`;
    }
    return `Dawn v${VERSION}`;
  }

  createMaster() {
    if (this.props.fieldControlStatus) {
      return this.props.masterStatus;
    }
    return false;
  }

  render() {
    return (
      <Navbar fixedTop fluid>
        <UpdateBox
          isRunningCode={this.props.isRunningCode}
          connectionStatus={this.props.connectionStatus}
          runtimeStatus={this.props.runtimeStatus}
          masterStatus={this.props.masterStatus}
          shouldShow={this.state.showUpdateModal}
          ipAddress={this.props.ipAddress}
          hide={this.toggleUpdateModal}
        />
        <ConfigBox
          shouldShow={this.state.showConfigModal}
          ipAddress={this.props.ipAddress}
          hide={this.toggleConfigModal}
        />
        <Navbar.Header>
          <Navbar.Brand id="header-title">
            {this.createHeader()}
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
          {this.props.runtimeStatus ?
            <Navbar.Text id="runtime-version">
              <Label bsStyle="info">{
                `Runtime v${this.props.runtimeVersion}: ${runtimeState[this.props.robotState]}`
              }
              </Label>
            </Navbar.Text> : ''
          }
          <Navbar.Text id="battery-indicator">
            <StatusLabel
              connectionStatus={this.props.connectionStatus}
              runtimeStatus={this.props.runtimeStatus}
              masterStatus={this.props.masterStatus}
              blueMaster={this.props.blueMaster}
              goldMaster={this.props.goldMaster}
              ipAddress={this.props.ipAddress}
              fieldControlStatus={this.props.fieldControlStatus}
            />
          </Navbar.Text>
          <Navbar.Form
            pullRight
          >
            <ButtonToolbar>
              <ButtonGroup>
                <TooltipButton
                  placement="bottom"
                  text="Tour"
                  bsStyle="info"
                  onClick={this.props.startTour}
                  id="tour-button"
                  glyph="info-sign"
                  disabled={false}
                />
                <TooltipButton
                  placement="bottom"
                  text="Robot IP"
                  bsStyle="info"
                  onClick={this.toggleConfigModal}
                  id="update-address-button"
                  glyph="transfer"
                  disabled={false}
                />
                <TooltipButton
                  placement="bottom"
                  text="Upload Upgrade"
                  bsStyle="info"
                  onClick={this.toggleUpdateModal}
                  disabled={!this.props.runtimeStatus}
                  id="update-software-button"
                  glyph="cloud-upload"
                />
              </ButtonGroup>
            </ButtonToolbar>
          </Navbar.Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
}

DNavComponent.propTypes = {
  connectionStatus: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  masterStatus: PropTypes.bool.isRequired,
  isRunningCode: PropTypes.bool.isRequired,
  ipAddress: PropTypes.string.isRequired,
  startTour: PropTypes.func.isRequired,
  runtimeVersion: PropTypes.string.isRequired,
  robotState: PropTypes.number.isRequired,
  heart: PropTypes.bool.isRequired,
  fieldControlStatus: PropTypes.bool.isRequired,
  blueMaster: PropTypes.number.isRequired,
  goldMaster: PropTypes.number.isRequired,
};

const mapStateToProps = state => ({
  masterStatus: state.fieldStore.masterStatus,
  blueMaster: state.fieldStore.blueMaster,
  goldMaster: state.fieldStore.goldMaster,
  robotState: state.info.robotState,
  heart: state.fieldStore.heart,
  ipAddress: state.info.ipAddress,
  fieldControlStatus: state.fieldStore.fieldControl,
  runtimeVersion: state.peripherals.runtimeVersion,
});


const DNav = connect(mapStateToProps)(DNavComponent);

export default DNav;
