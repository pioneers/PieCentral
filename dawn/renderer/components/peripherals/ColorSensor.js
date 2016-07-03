import React from 'react';
import {
  OverlayTrigger,
  Popover,
} from 'react-bootstrap';
import numeral from 'numeral';
import NameEditContainer from '../NameEditContainer';
import _ from 'lodash';

/**
 * A component representing the ColorSensor. Test.
 */
class ColorSensor extends React.Component {
  constructor(props) {
    super(props);
    this.getHexColorValue = this.getHexColorValue.bind(this);
  }

  /**
   * Convert the separate R, G, B integer values to hex representation,
   * with the format '#RRGGBB'.
   */
  getHexColorValue() {
    const hexRepresentation = _.map(_.slice(this.props.value, 0, 3), (val) => {
      const hexVal = val.toString(16);
      return hexVal.length === 1 ? `0${hexVal}` : hexVal;
    }).join('');
    return `#${hexRepresentation}`;
  }

  render() {
    return (
      <div style={{ overflow: 'auto' }}>
        <div style={{ overflow: 'auto', width: '100%' }}>
          <h4 style={{ float: 'left' }}>
            <NameEditContainer name={this.props.name} id={this.props.id} />
            <small> {this.props.peripheralType} </small>
          </h4>
          <OverlayTrigger
            trigger={['hover', 'focus']}
            placement="left"
            overlay={
              <Popover id="colors">
                {`R: ${this.props.value[0]} G: ${this.props.value[1]} B: ${this.props.value[2]}`}
                <br />
                {`Hue: ${numeral(this.props.value[4]).format('0.00')}`}
                <br />
                {`Luminosity: ${numeral(this.props.value[3]).format('0.00')}`}
              </Popover>
            }
          >
            <div
              style={{
                float: 'right',
                width: '35px',
                height: '35px',
                backgroundColor: this.getHexColorValue(),
              }}
            >
            </div>
          </OverlayTrigger>
        </div>
      </div>
    );
  }
}

ColorSensor.propTypes = {
  name: React.PropTypes.string,
  peripheralType: React.PropTypes.string,
  id: React.PropTypes.string,
  value: React.PropTypes.array,
};

export default ColorSensor;
