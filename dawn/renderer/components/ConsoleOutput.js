import React from 'react';
import { Panel } from 'react-bootstrap';

class ConsoleOutput extends React.Component {
  componentWillReceiveProps(nextProps) {
    if (this.props.output.size === 0 && nextProps.output.size > 0 && !this.props.show) {
      this.props.toggleConsole();
    }
  }

  render() {
    const height = `${String(this.props.height)}px`;
    return (
      <div>
        <Panel collapsible expanded={this.props.show}>
          <pre style={{ position: 'relative', height }}>
            <div
              style={{
                position: 'absolute',
                bottom: '0',
                maxHeight: height,
                overflowY: 'auto',
                padding: '5px',
                width: '99%',
              }}
            >
            {this.props.output.map((line, index) => (
              <code key={index}>{line}</code>
            ))}
            </div>
          </pre>
        </Panel>
      </div>
    );
  }
}

ConsoleOutput.propTypes = {
  height: React.PropTypes.number,
  output: React.PropTypes.array,
  toggleConsole: React.PropTypes.func,
  show: React.PropTypes.bool,
};

export default ConsoleOutput;
