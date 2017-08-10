import React from 'react';


class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {};
    this.props.fetchDataPeriodically((data) => this.setState(data));
  }

  render() {
    console.log('App.render()');

    // For each score component, find the score for that fixture in the newly
    // fetched data and set it in the component's state.
    for(var i=0; i < this.props.scoreComponents.length; i++) {
      var score = this.props.scoreComponents[i];
      var fixture = this.state[score.props.fixtureID];
      if(fixture) {
        score.setState({score: fixture.score});
      }
    }
    return null;
  }

}
export default App;
