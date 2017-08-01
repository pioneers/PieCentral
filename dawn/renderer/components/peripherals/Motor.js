import PropTypes from 'prop-types';
import _ from 'lodash';
import numeral from 'numeral';

import { ProgressBar } from 'react-bootstrap';

/**
 *  Motor Component
 */
const Motor = props => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}>
        <div>{props.id}</div>
        <small>{'Motor'}</small>
      </h4>
      {
        _.map(props.param, obj => ( // TODO: Figure out if a ProgressBar is useful
          <div key={`${obj.param}-${props.device_name}-Overall`}>
            <h4 style={{ float: 'right', height: '10px' }} key={`${obj.param}-${props.device_name}`}>
              {`${obj.param}: ${numeral(obj.float_value).format('+0.00')}`}
              <ProgressBar now={obj.float_value} min={-100} />
            </h4>
            <div style={{ clear: 'both', height: '2px' }} key={`${obj.param}-${props.device_name}-Spacing`} />
          </div>
        ))
      }
    </div>
  </div>
);

Motor.propTypes = {
  device_name: PropTypes.string,
  id: PropTypes.string,
  param: PropTypes.array,
};

export default Motor;
