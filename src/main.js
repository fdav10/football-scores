import React from 'react';
import ReactDOM from 'react-dom';
import Score from './Score';


function fetchFixtureData(success) {
  console.log('fetchFixtureData');
  $.ajax({
    url: '/json/fixture_updates',
    type: 'GET',
    success: success,
    error: () => { console.log('Error fetching fixture data') }
  })
}


function createScoreComponents() {
  // Attach a Score component to each score mount point
  var fixtures = document.getElementsByClassName('fixture-row');

  for(var i=0; i < fixtures.length; i++) {

    var fixture = fixtures[i];

    // get score elements
    var scoreMount = fixture.getElementsByClassName('score-mount')[0]

    // Delete existing score
    scoreMount.innerHTML = '';

    // Attach Score component
    ReactDOM.render(
      <Score fixtureID={fixture.id.replace('fixture-', '')} />,
      scoreMount
    );
  }
}

// Subsequently: just fetch fixture data
function fetchFixtureDataPeriodically() {
  fetchFixtureData((data) => {
    /* console.log('fetchFixtureData callback');*/
    document.fixtureData = data;
    // FIXME: Don't know how to make existing components re-render
    createScoreComponents()
  });
  setTimeout(fetchFixtureDataPeriodically, 1000 * 5);
}

// First time: fetch fixture data and create Score components
document.addEventListener('DOMContentLoaded', () => {
  fetchFixtureData((data) => {
    console.log('fetchFixtureData callback (on page load)');
    document.fixtureData = data;
    createScoreComponents();
    fetchFixtureDataPeriodically();
  })
});
