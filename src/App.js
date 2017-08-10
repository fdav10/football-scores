import React from 'react';


class App extends React.Component {

  constructor() {
    super();
    this.state = {};
    this.fetchDataPeriodically = this.fetchDataPeriodically.bind(this);
    this.onFetch = this.onFetch.bind(this);
    this.setState = this.setState.bind(this);
  }

  setState(state) {
    console.log('setState(): ' + state);
    React.Component.prototype.setState(state);
  }

  onFetch(data) {
    this.setState(data);
  }

  fetchDataPeriodically() {
    this.props.fetchDataPeriodically((data) => this.onFetch(data))
  }

  render() {
    console.log('App.render()');

    // For each score component, find the score for that fixture in the newly
    // fetched data and set it in the component's state.
    for(var i=0; i < this.props.scoreComponents; i++) {
      var score = this.props.scoreComponents[i];
      score.setState({
        score: this.state[score.props.fixtureID].score
      });
    }
    return null;
  }

}
export default App;
