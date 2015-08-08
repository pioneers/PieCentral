jest.dontMock('../MotorTester.js');

describe('MotorTester', function () {
  it('generates fake data', function () {
    var React = require('react/addons');
    var MotorTester = require('../MotorTester.js');
    var RobotActions = require('../../actions/RobotActions');
    var TestUtils = React.addons.TestUtils;

    var tester = TestUtils.renderIntoDocument(
      <MotorTester />
      );

    tester.generateFakeData();
    expect(RobotActions.updateMotor).toBeCalled();
  });
});
