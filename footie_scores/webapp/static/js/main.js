function showSubList () {
  var slideUp = $(this).next().css('display') === 'block';
  console.log(slideUp);
  $(".sub-list").slideUp(150);
  if (slideUp) {
    $(this).next().slideUp(150);
  } else {
    $(this).next().slideDown(150);
  }
}

function filterCompetitions () {
  $(".competition-container").hide();
  var competition = $(this).text().replace(/ /g, "-");
  console.log("#" + competition)
  $("#" + competition).show();
}

function showAllCompetitions () {
  $(".competition-container").show();
  console.log("all comps pressed");
}



$( document ).ready(function() {
  $(".sidebar strong").on("click", showSubList);
  $(".sidebar .sub-list li.individual-competitions").on("click", filterCompetitions);
  $(".sidebar .sub-list li#all-comps-button").on("click", showAllCompetitions);
});

