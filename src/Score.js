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
    this.scoreOrLocalTime = convertUtcToLocal(this.state.score)
    return (
        <div className="score mui-col-xs-2">
	    <h4 style={{color: "black"}}>{this.scoreOrLocalTime}</h4>
	</div>
    )
  }

}
export default Score;
