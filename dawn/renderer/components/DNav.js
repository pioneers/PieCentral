import React from 'react';
import { connect } from 'react-redux';
import {
  Navbar,
  ButtonToolbar,
  ButtonGroup,
  Label } from 'react-bootstrap';
import IPBox from './IPBox';
import UpdateBox from './UpdateBox';
import StatusLabel from './StatusLabel';
import TooltipButton from './TooltipButton';
import { REG_VERSION, FC_VERSION } from '../constants/Constants';
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
      return `Dawn v${FC_VERSION} ${(this.props.heart) ? '+' : '-'}`;
    }
    return `Dawn v${REG_VERSION}`;
  }

  render() {
    return (
      <Navbar fixedTop fluid>
        <UpdateBox
          isRunningCode={this.props.isRunningCode}
          connectionStatus={this.props.connection}
          runtimeStatus={this.props.runtimeStatus}
          shouldShow={this.state.showUpdateModal}
          ipAddress={this.props.ipAddress}
          hide={this.toggleUpdateModal}
        />
        <IPBox
          shouldShow={this.state.showConfigModal}
          ipAddress={this.props.ipAddress}
          onIPChange={this.props.onIPChange}
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
              connectionStatus={this.props.connection}
              runtimeStatus={this.props.runtimeStatus}
              battery={this.props.battery}
              batterySafety={this.props.batterySafety}
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
                />
                <TooltipButton
                  placement="bottom"
                  text="Robot IP"
                  bsStyle="info"
                  onClick={this.toggleConfigModal}
                  id="update-address-button"
                  glyph="transfer"
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
  connection: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  battery: React.PropTypes.number,
  batterySafety: React.PropTypes.bool,
  isRunningCode: React.PropTypes.bool,
  ipAddress: React.PropTypes.string,
  startTour: React.PropTypes.func,
  onIPChange: React.PropTypes.func,
  runtimeVersion: React.PropTypes.string,
  robotState: React.PropTypes.number,
  heart: React.PropTypes.bool,
  fieldControlStatus: React.PropTypes.bool,
};

const mapStateToProps = state => ({
  robotState: state.info.robotState,
  heart: state.fieldStore.heart,
  fieldControlStatus: state.fieldStore.fieldControl,
});


const DNav = connect(mapStateToProps)(DNavComponent);

export default DNav;
