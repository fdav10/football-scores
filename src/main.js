import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import Score from './Score';
import UpdateTimer from './UpdateTimer';


function fetchFixtureData(success) {
  console.log('fetchFixtureData');
  $.ajax({
    url: '/json/fixture_updates',
    type: 'GET',
    success: success,
    error: () => { console.log('Error fetching fixture data') }
  })
}


function fetchFixtureDataPeriodically(success) {
  fetchFixtureData(success);
  setTimeout(() => fetchFixtureDataPeriodically(success), 1000 * 5);
}


function createScoreComponents() {
  // Attach a Score component to each score mount point
  var fixtures = document.getElementsByClassName('fixture-row');

  var scoreComponents = []

  for(var i=0; i < fixtures.length; i++) {

    var fixture = fixtures[i];

    // get score elements
    var scoreMount = fixture.getElementsByClassName('score-mount')[0]

    // Attach Score component
    var score = ReactDOM.render(
      <Score
	fixtureID={fixture.id.replace('fixture-', '')}
	initial_score={scoreMount.innerText}
      />,
      scoreMount
    );
    scoreComponents.push(score);
  }

  var updateTimer = ReactDOM.render(
    <UpdateTimer tickPeriod={1 * 1000} />,
    document.getElementById('update-timer-mount'),
  )
  updateTimer.tick();

  var app = ReactDOM.render(
    <App
      scoreComponents={scoreComponents}
      updateTimerComponent={updateTimer}
      fetchDataPeriodically={fetchFixtureDataPeriodically}
    />,
    document.getElementById('app-mount'),
  );

}

// First time: fetch fixture data and create Score components
document.addEventListener('DOMContentLoaded', () => {
  fetchFixtureData((data) => {
    console.log('fetchFixtureData callback (on page load)');
    createScoreComponents();
  })
});
