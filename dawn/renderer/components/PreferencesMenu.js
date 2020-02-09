import React from 'react';
import {
  Button,
  Card,
  Drawer,
  FormGroup,
  H1,
  H2,
  HTMLSelect,
  InputGroup,
  NumericInput,
  Switch,
} from '@blueprintjs/core';
import { IconNames } from '@blueprintjs/icons';

class PreferencesMenu extends React.Component {
  constructor() {
    super();
    this.state = { isOpen: false };
  }

  render() {
    return (
      <div>
        <Button icon={IconNames.SETTINGS} onClick={() => this.setState({ isOpen: true })}>Preferences</Button>
        <Drawer isOpen={this.state.isOpen} onClose={() => this.setState({ isOpen: false })}>
          <H1>Preferences</H1>
          <Card>
            <H2>Robot</H2>
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
          </Card>
          <Card>
            <H2>Editor</H2>
            <FormGroup label="Dark Theme" inline>
              <Switch
                checked={this.props.dark}
                onChange={() => console.log('OK!')}
              />
            </FormGroup>
            <FormGroup label="Editor theme" inline helperText="Color palette for the text editor">
              <HTMLSelect options={['Monokai']} />
            </FormGroup>
          </Card>
        </Drawer>
      </div>
    );
  }
}

export default PreferencesMenu;
