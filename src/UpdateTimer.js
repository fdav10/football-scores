import React from 'react';


class UpdateTimer extends React.Component {

  constructor(props) {
    super(props);
    this.state = {};
    this.tick = this.tick.bind(this);
  }

  tick() {
    this.setState({
      currentTime: (new Date).getTime()
    });
    setTimeout(this.tick, this.props.tickPeriod);
  }

  render() {
    return (
        <p>
          Last updated: {Math.round((this.state.currentTime - this.state.lastUpdatedTime) / 1000)} seconds ago
        </p>
    )
  }

}
export default UpdateTimer;
