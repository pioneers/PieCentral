import React from 'react';
import PropTypes from 'prop-types';
import { Panel } from 'react-bootstrap';

class ConsoleOutput extends React.Component {
  constructor(props) {
    super(props);
    this.scrollToBottom = this.scrollToBottom.bind(this);
  }

  componentDidMount() {
    this.scrollToBottom();
  }

  componentDidUpdate(prevProps) {
    this.scrollToBottom();
    if (prevProps.output.size === 0 && this.props.output.size > 0 && !prevProps.show) {
      this.props.toggleConsole();
    }
  }

  scrollToBottom() {
    if (!this.props.disableScroll) {
      this.outerDiv.scrollTop = this.outerDiv.scrollHeight;
    }
  }

  render() {
    const height = `${String(this.props.height)}px`; // TODO: Use Panel.Collapse
    return (
      <div>
        <Panel
          style={{
            display: this.props.show ? 'block' : 'none',
            marginBottom: '0',
            borderRadius: '0',
          }}
        >
          <Panel.Body>
            <pre
              style={{
                position: 'relative',
                margin: '0',
                height,
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  bottom: '0',
                  maxHeight: height,
                  overflowY: 'auto',
                  padding: '20px',
                  width: '99%',
                }}
                ref={(el) => { this.outerDiv = el; }}
              >
                {this.props.output.map((line) => (
                  <code key={`${line}-Code-${Math.random()}`}>{line}</code>
                ))}
              </div>
            </pre>
          </Panel.Body>
        </Panel>
      </div>
    );
  }
}

ConsoleOutput.propTypes = {
  height: PropTypes.number.isRequired,
  output: PropTypes.array.isRequired,
  toggleConsole: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  disableScroll: PropTypes.bool.isRequired,
};

export default ConsoleOutput;
