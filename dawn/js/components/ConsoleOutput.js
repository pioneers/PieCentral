import React from 'react';
import {
  Panel,
  Accordion,
  Button,
  ButtonGroup,
  ButtonToolbar
} from 'react-bootstrap';
import _ from 'lodash';

var ConsoleOutput = React.createClass({
  render() {
    return (
      <div>
        <Panel collapsible expanded={this.props.show}>
          <pre style={{position: 'relative', height: this.props.height}}>
            <div style={{
                position: 'absolute',
                bottom: '0',
                maxHeight: this.props.height,
                overflowY: 'auto',
                padding: '5px',
                width: '99%'
            }}>
            {_.map(this.props.output, (line, index)=>{
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
