import React from 'react';
import PropTypes from 'prop-types';
import { Panel } from 'react-bootstrap';

class ConsoleOutput extends React.Component {
  static getHeight() {
    return 100;
  }
  constructor(props) {
    super(props);
    this.scrollToBottom = this.scrollToBottom.bind(this);
  }

  componentDidMount() {
    this.scrollToBottom();
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.output.size === 0 && nextProps.output.size > 0 && !this.props.show) {
      this.props.toggleConsole();
    }
  }

  componentDidUpdate() {
    this.scrollToBottom();
  }

  scrollToBottom() {
    if (!this.props.disableScroll) {
      this.outerDiv.scrollTop = this.outerDiv.scrollHeight;
    }
  }


  render() {
    const height = `${String(this.props.height)}px`; // TODO: Use Panel.Collapse
    return (
      <Panel
        id="console-panel"
        style={{
            display: this.props.show ? 'block' : 'none',
            marginBottom: '0',
            borderRadius: '0',
            width: '1000px',
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
                  overflowY: 'auto',
                  padding: '20px',
                  width: '1000px',
                }}
              ref={(el) => { this.outerDiv = el; }}
            >
              {this.props.output.map(line => (
                <code key={`${line}-Code-${Math.random()}`}>{line}</code>
                ))}
            </div>
            <div>
                Height is {this.props.editorHeight};
            </div>
          </pre>
        </Panel.Body>
      </Panel>
    );
  }
}

ConsoleOutput.propTypes = {
  height: PropTypes.number.isRequired,
  editorHeight: PropTypes.number.isRequired,
  output: PropTypes.array.isRequired,
  toggleConsole: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  disableScroll: PropTypes.bool.isRequired,
};

export default ConsoleOutput;
