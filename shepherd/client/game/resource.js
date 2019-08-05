import React from 'react';
import { createAction, handleAction } from 'redux-actions';
import { Row, Col } from 'react-grid-system';
import { connect } from 'react-redux';
import {
  Card,
  H2,
  HTMLTable,
} from '@blueprintjs/core';
import { RESOURCE_TYPE, RESOURCE_STATUS } from '../util';

const UPDATE_RESOURCES = 'UPDATE_RESOURCES';
export const updateResources = createAction(UPDATE_RESOURCES);
export const handleResourcesUpdate = handleAction(
  UPDATE_RESOURCES, (state, action) => action.payload, []);

class ResourceStatusTable extends React.Component {
  render() {
    console.log(this.props.resources);
    return (
      <div>
        <H2>Resources</H2>
        <Row>
          <Col>
            <HTMLTable striped style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Last Heartbeat</th>
                </tr>
              </thead>
              <tbody>
                { (this.props.resources || []).map((resource, index) => (
                  <tr key={index}>
                    <td>{ resource.name }</td>
                    <td>{ RESOURCE_TYPE[resource.type] || '(Unknown)' }</td>
                    <td>{ RESOURCE_STATUS[resource.status] || '(Unknown)' }</td>
                    <td>{ new Date().toISOString() }</td>
                  </tr>
                )) }
              </tbody>
            </HTMLTable>
          </Col>
        </Row>
      </div>
    );
  }
}

export default connect(
  state => ({ resources: state.resources }),
)(ResourceStatusTable);
