import React from 'react';

class Score extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      score: this.props.initial_score
    };
  }

  render() {
    console.log('Score.render() for fixtureID = ' + this.props.fixtureID);
    return (
        <div className="score mui-col-xs-2">
          <h4>{this.state.score}</h4>
        </div>
    )
  }

}
export default Score;
