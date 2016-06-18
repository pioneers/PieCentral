import React from 'react';
import {
  Button,
  DropdownButton,
  MenuItem,
  ButtonGroup,
  ButtonToolbar,
  Glyphicon,
  OverlayTrigger,
  Tooltip,
  Modal
} from 'react-bootstrap';
import {ipcRenderer} from 'electron';
import Ansible from '../utils/Ansible';
import _ from 'lodash';

export default React.createClass({
  propTypes: {
    buttons: React.PropTypes.array.isRequired,
    unsavedChanges: React.PropTypes.bool.isRequired
  },
  getInitialState() {
    return {
      gameMode: -1,
      showModal: false,
      simulating: false
    };
  },
  componentDidMount() {
    ipcRenderer.on('simulate-competition', (event, args)=>{
      this.openModal();
    });
  },
  openModal() {
    this.setState({showModal: true});
  },
  closeModal() {
    this.setState({showModal: false});
  },
  renderToolbar() {
    return (
      _.map(this.props.buttons, (group, groupIndex) => {
        return (
          <ButtonGroup key={String(groupIndex)} id={group.groupId}>
            {_.map(group.buttons, (button, buttonIndex) => {
              return button.render(String(groupIndex) + String(buttonIndex));
            })}
          </ButtonGroup>
        );
      })
    );
  },
  gameModes: [
    {enabled: true, autonomous: true, name: 'autonomous'}, // autonomous mode
    {enabled: false, autonomous: true, name: 'disabled'}, // autonomous disabled mode
    {enabled: true, autonomous: false, name: 'teleop'} // teleop mode
  ],
  changeGameMode(mode) {
    Ansible.sendMessage('game', this.gameModes[mode]);
    this.setState({gameMode: mode});
  },
  cancelSimulation() {
    this.changeGameMode(2);
    Ansible.sendMessage('stop', {});
    this.setState({simulating: false});
    _(this.state.timeouts).forEach((tId)=>{
      clearTimeout(tId);
    });
  },
  simulateGamemodes() {
    // autonomous disabled
    this.changeGameMode(1);
    this.setState({simulating: true});
    let t1 = setTimeout(()=>{
      this.changeGameMode(0);
      Ansible.sendMessage('execute', {});
    }, 5000);
    let t2 = setTimeout(()=>{
      this.changeGameMode(1);
    }, 35000);
    let t3 = setTimeout(()=>{
      this.changeGameMode(2);
    }, 45000);
    let t4 = setTimeout(()=>{
      Ansible.sendMessage('stop', {});
      this.setState({simulating: false});
    }, 75000);
    this.setState({timeouts: [t1, t2, t3, t3]});
  },
  render() {
    let simulationStatus = null;
    if (!this.props.runtimeStatus) {
      simulationStatus = 'Not connected to runtime';
    } else if (this.state.simulating) {
      simulationStatus = this.gameModes[this.state.gameMode].name;
    } else {
      simulationStatus = 'Idle';
    }
    return (
      <div>
        <ButtonToolbar id="editor-toolbar">
          { this.renderToolbar() }
          <DropdownButton
            disabled={!this.props.runtimeStatus}
            title="Mode"
            bsSize="small"
            id="choose-mode">
            <MenuItem
              active={this.state.gameMode == 0}
              onClick={()=>this.changeGameMode(0)}
              key={0}>Autonomous</MenuItem>
            <MenuItem
              active={this.state.gameMode == 1}
              onClick={()=>this.changeGameMode(1)}
              key={1}>Disabled</MenuItem>
            <MenuItem
              active={this.state.gameMode == 2}
              onClick={()=>this.changeGameMode(2)}
              key={2}>TeleOp</MenuItem>
          </DropdownButton>
          <DropdownButton
            title="Theme"
            bsSize="small"
            id="choose-theme">
            { _.map(this.props.themes, (theme, index) => {
              return (
                <MenuItem
                  active={theme == this.props.editorTheme}
                  onClick={_.partial(this.props.changeTheme, theme)}
                  key={index}>
                  {theme}
                </MenuItem>
              );
            }) }
          </DropdownButton>
        </ButtonToolbar>
        <Modal show={this.state.showModal}>
          <Modal.Header>
            <Modal.Title>Simulating Competition</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>
              This tool simulates the process of a competition. It runs
              your code in autonomous for 30 seconds, pauses for 10 seconds,
              and then runs your code in teleop for 30 seconds (in actual
              competition, teleop lasts 2 minutes)
            </p>
            <p>
              <Button
                onClick={this.simulateGamemodes}
                bsStyle="primary"
                disabled={!this.props.runtimeStatus || this.state.simulating}>
                Start simulation
              </Button>
              <Button
                onClick={this.cancelSimulation}
                bsStyle="warning"
                disabled={!this.state.simulating}>
                Cancel Simulation
              </Button>
            </p>
            <p>Status: {simulationStatus}</p>
          </Modal.Body>
          <Modal.Footer>
            <Button
              onClick={this.closeModal}
              disabled={this.state.simulating}>
              Close
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
});
