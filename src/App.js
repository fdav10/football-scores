import React from 'react';


class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {};
    this.props.fetchDataPeriodically((data) => {
      var now = (new Date).getTime();
      data.lastUpdatedTime = now;
      this.setState(data);
      this.props.updateTimerComponent.setState({
        currentTime: now,
        lastUpdatedTime: now
      })
    });
  }

  componentWillUpdate() {
    console.log('Pre App.render()');

    // For each score component, find the score for that fixture in the newly
    // fetched data and set it in the component's state.
    for(var i=0; i < this.props.scoreComponents.length; i++) {
      var score = this.props.scoreComponents[i];
      var fixture = this.state[score.props.fixtureID];
      if(fixture) {
	if(fixture.override_score){
	  fixture.score = fixture.override_score;
	}
        score.setState({score: fixture.score});
      }
    }
  }

  render() {
    console.log('App.render()');
    return null;
  }

}
export default App;
