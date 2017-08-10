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

  document.scoreComponents = [];

  for(var i=0; i < fixtures.length; i++) {

    var fixture = fixtures[i];

    // get score elements
    var scoreMount = fixture.getElementsByClassName('score-mount')[0]

    // Delete existing score
    scoreMount.innerHTML = '';

    // Attach Score component
    var score = <Score fixtureID={fixture.id.replace('fixture-', '')} />;
    document.scoreComponents.push(score);
    ReactDOM.render(
      score,
      scoreMount
    );
  }
}


function renderAll() {
  // FIXME: This doesn't work
  for(var i=0; i < document.scoreComponents.length; i++) {
    console.log('renderAll() ' + document.scoreComponents[i].fixtureID);
    document.scoreComponents[i].render();
  }
}


// First time: fetch fixture data and create Score components
document.addEventListener('DOMContentLoaded', () => {
  fetchFixtureData((data) => {
    console.log('fetchFixtureData callback (on page load)');
    document.fixtureData = data;
    createScoreComponents();
  })
});


// Subsequently: just fetch fixture data
(function fetchFixtureDataPeriodally() {
  console.log('fetchFixtureDataPeriodally()');
  fetchFixtureData((data) => {
    console.log('fetchFixtureData callback');
    document.fixtureData = data;
    // FIXME: Don't know how to make existing components re-render
    // renderAll();
    createScoreComponents()
  });
  setTimeout(fetchFixtureDataPeriodally, 1000 * 5);
})()
