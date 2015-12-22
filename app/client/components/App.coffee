React = require('react')
Joyride = require('react-joyride')
Router = require('react-router')
DNav = require('./DNav')
Dashboard = require('./Dashboard')

module.exports = Dawn = React.createClass
  displayName: 'Dawn'

  getInitialState: ->
    steps: []

  addSteps: (steps) ->
    joyride = this.refs.joyride

    if not Array.isArray(steps)
      steps = [steps]

    if not steps.length
      return false

    this.setState((currentState) ->
      currentState.steps = currentState.steps.concat(joyride.parseSteps(steps))
      return currentState
    )

  addTooltip: (data) ->
    this.refs.joyride.addTooltip(data)

  startTour: ->
    this.refs.joyride.start(false)

  componentDidMount: ->
    this.addSteps([{
      title: 'Editor',
      text: 'This is the code editor. Create and edit your robot\'s code here.',
      selector: '.ace_editor',
      position: 'bottom-left',
      type: 'hover'
    },{
      title: 'Gamepads',
      text: 'This panel displays all the connected gamepads.',
      selector: '#gamepads-panel',
      position: 'left',
      type: 'hover'
    },{
      title: 'Peripherals',
      text: 'This panel displays info about your robot\'s peripherals, including motors and sensors.',
      selector: '#peripherals-panel',
      position: 'left',
      type: 'hover'
    }])

  render: ->
    <div>
      <Joyride ref="joyride" steps={this.state.steps} />
      <DNav {...this.props} startTour={this.startTour}/>
      <div style={height: '60px', marginBottom: '21px'}/>
      {React.cloneElement(this.props.children, {
        addSteps: this.addSteps,
        addTooltip: this.addTooltip
      })}
    </div>
