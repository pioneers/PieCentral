import React from 'react';
import { connect } from 'react-redux';
import {
  Button,
  Card,
  Classes,
  Drawer,
  FormGroup,
  H2,
  H3,
  HTMLSelect,
  InputGroup,
  Intent,
  NumericInput,
  Slider,
  Switch,
} from '@blueprintjs/core';
import { IconNames } from '@blueprintjs/icons';

import { toggleDarkTheme } from '../actions/preferences';

class Preferences extends React.Component {
  constructor() {
    super();
    this.state = { isOpen: false };
    this.close = this.close.bind(this);
    this.open = this.open.bind(this);
    this.confirm = this.confirm.bind(this);
  }

  close() {
    this.setState({ isOpen: false });
  }

  open() {
    this.setState({ isOpen: true });
  }

  confirm() {
    this.close();
  }

  render() {
    return (
      <div>
        <Button icon={IconNames.SETTINGS} onClick={this.open}>Preferences</Button>
        <Drawer
            className={this.props.darkTheme ? Classes.DARK : Classes.LIGHT}
            isOpen={this.state.isOpen}
            onClose={this.close}
            icon={IconNames.SETTINGS}
            title="Preferences"
        >
          <div className={Classes.DRAWER_BODY}>
            <div className={Classes.DIALOG_BODY}>
              <H3>Robot</H3>
              <FormGroup label="Team Number" inline>
                <NumericInput placeholder="Example: 42" min={0} max={100} />
              </FormGroup>
              <FormGroup
                label="IP Address"
                inline
                labelInfo="(optional)"
                helperText="Overrides the automatic address calculation."
              >
                <InputGroup placeholder="Example: 192.168.1.1" />
              </FormGroup>
              <H3>Editor</H3>
              <FormGroup label="Dark Theme" inline>
                <Switch
                  checked={this.props.darkTheme}
                  onChange={this.props.toggleDarkTheme}
                />
              </FormGroup>
              <FormGroup label="Color palette" inline>
                <HTMLSelect options={['Monokai']} />
              </FormGroup>
              <FormGroup label="Text size" inline>
                <Slider min={10} max={50} value={this.props.editor.textSize} labelStepSize={10} />
              </FormGroup>
              <H3>Console</H3>
              <FormGroup label="Max lines" inline helperText="Truncate the console to this many lines.">
                <NumericInput min={10} max={1000} value={this.props.console.maxLines} />
              </FormGroup>
            </div>
          </div>
          <div className={Classes.DRAWER_FOOTER}>
            <Button
              text="Confirm"
              icon={IconNames.TICK_CIRCLE}
              intent={Intent.SUCCESS}
              onClick={this.confirm}
              large
            />
          </div>
        </Drawer>
      </div>
    );
  }
}

export default connect(
  state => ({ ...state.preferences }),
  { toggleDarkTheme },
)(Preferences);
