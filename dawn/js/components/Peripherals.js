import React from 'react';
import NameEdit from './NameEdit';
import {
  Button,
  OverlayTrigger,
  Popover,
  ProgressBar
} from 'react-bootstrap';
import { PeripheralTypes } from '../constants/Constants';
import numeral from 'numeral';
import _ from 'lodash';


/**
 * A component representing the ColorSensor. Test.
 */
export class ColorSensor extends React.Component {
  constructor(props) {
    super(props);
  }

  /**
   * Convert the separate R, G, B integer values to hex representation,
   * with the format '#RRGGBB'.
   */
  getHexColorValue() {
    let hexRepresentation = _.map(_.slice(this.props.value, 0, 3), (val)=>{
      let hexVal = val.toString(16);
      return hexVal.length === 1 ? '0' + hexVal : hexVal;
    }).join('');
    return '#' + hexRepresentation;
  }

  render() {
    return (
      <div style={{overflow: 'auto'}}>
        <div style={{overflow: 'auto', width: '100%'}}>
          <h4 style={{float: 'left'}}>
            <NameEdit name={this.props.name} id={this.props.id} />
            <small> {this.props.peripheralType} </small>
          </h4>
          <OverlayTrigger trigger={["hover", "focus"]} placement="left" overlay={
            <Popover id="colors">
              {`R: ${this.props.value[0]} G: ${this.props.value[1]} B: ${this.props.value[2]}`}
              <br/>
              {`Hue: ${numeral(this.props.value[4]).format('0.00')}`}
              <br/>
              {`Luminosity: ${numeral(this.props.value[3]).format('0.00')}`}
            </Popover>
          }>
            <div style={{
              float: 'right',
              width: '35px',
              height: '35px',
              backgroundColor: this.getHexColorValue()}}>
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
  value: React.PropTypes.array
};


/**
 * A component representing a boolean sensor,
 * for example a LimitSwitch.
 */
export class BooleanSensor extends React.Component {
  constructor(props) {
    super(props);
  }

  /**
   * Formats data for display based on peripheralType.
   */
  formatBoolean(peripheralType, sensorValue) {
    if (peripheralType === PeripheralTypes.LimitSwitch) {
      return (sensorValue) ? "Open" : "Closed";
    } else {
      return sensorValue;
    };
  }

  render() {
    return (
      <div style={{overflow: 'auto'}}>
        <div style={{overflow: 'auto', width: '100%'}}>
          <h4 style={{float: 'left'}}><NameEdit name={this.props.name} id={this.props.id} /><small> {this.props.peripheralType} </small></h4>
          <h4 style={{float: 'right'}}> {this.formatBoolean(this.props.peripheralType, this.props.value)} </h4>
        </div>
      </div>
    );
  }
}

BooleanSensor.propTypes = {
  name: React.PropTypes.string,
  peripheralType: React.PropTypes.string,
  id: React.PropTypes.string,
  value: React.PropTypes.number
};


/**
 * A component representing a motor.
 */
export class Motor extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div style={{overflow: 'auto'}}>
        <div style={{overflow: 'auto', width: '100%'}}>
          <h4 style={{float: 'left'}}><NameEdit name={this.props.name} id={this.props.id} /><small> Motor</small></h4>
          <h4 style={{float: 'right'}}>
            {numeral(this.props.value).format('+0.00')}
          </h4>
        </div>
        <ProgressBar now={Math.abs(this.props.value)}></ProgressBar>
      </div>
    );
  }
}

Motor.propTypes = {
  name: React.PropTypes.string,
  value: React.PropTypes.number
};


export class ScalarSensor extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div style={{overflow: 'auto'}}>
        <div style={{overflow: 'auto', width: '100%'}}>
          <h4 style={{float: 'left'}}><NameEdit name={this.props.name} id={this.props.id} /><small> {this.props.peripheralType} </small></h4>
          <h4 style={{float: 'right'}}> {numeral(this.props.value).format('0.00')} </h4>
        </div>
      </div>
    );
  }
}

ScalarSensor.propTypes = {
  name: React.PropTypes.string,
  peripheralType: React.PropTypes.string,
  id: React.PropTypes.string,
  value: React.PropTypes.number
};


/**
 * A generic peripheral, used when the peripheralType is unknown.
 */
export class GenericPeripheral extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div style={{overflow: 'auto'}}>
        <div style={{overflow: 'auto', width: '100%'}}>
          <h4 style={{float: 'left'}}>
            <NameEdit name={this.props.name} id={this.props.id} />
            <small>{this.props.peripheralType}</small>
          </h4>
          <h4 style={{float: 'right'}}>
            { this.props.value }
          </h4>
        </div>
      </div>
    );
  }
}

GenericPeripheral.defaultProps = {
  peripheralType: 'peripheralType was undefined'
};
