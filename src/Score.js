import React from 'react';

class Score extends React.Component {

  render() {
    console.log('Score.render() for fixtureID = ' + this.props.fixtureID);
    return (
        <div className="score mui-col-xs-2">
          <h4>{document.fixtureData[this.props.fixtureID].score}</h4>
        </div>
    )
  }

}
export default Score;
