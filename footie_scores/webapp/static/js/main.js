
function showClickedSublist () {
  var slideUp = $(this).next().css('display') === 'block';
  $(".sub-list").slideUp(150);
  if (slideUp) {
    $(this).next().slideUp(150);
  } else {
    $(this).next().slideDown(150);
  }
}

function showNamedSublist (selector) {
  console.log(selector);
  $(selector).parent().show();
}

function filterCompetitions () {
  $(".competition-container").hide();
  var competition = $(this).text().replace(/ /g, "-");
  $("#" + competition).show();
}

function showAllCompetitions () {
  $(".competition-container").show();
}

sublistToShow = {
  '/todays_games': '#todays-games'
}

function toggleMainPanel () {
  mainPanelMargin = document.isMobileView ? '500px' : '-500px';
  marginLeft = $(".sidebar").css('display') == 'none' ? "0px" : mainPanelMargin;
  $(".main-panel").css({'margin-left': marginLeft});
}

function toggleSidebar() {
  sidebarLeftValue = parseInt($(".sidebar").css("left"))
  strScreenWidth = String(screen.width)
  leftAnimTarget = sidebarLeftValue < 0 ? "+=" + strScreenWidth : "-=" + strScreenWidth
  $(".sidebar").animate({left: leftAnimTarget});
}


$( document ).ready(function() {
  var htmlName = location.pathname;
  document.isMobileView = $(".sidebar").css('display') === 'none';
  showNamedSublist(sublistToShow[htmlName]);
  $(".sidebar strong").on("click", showClickedSublist);
  $(".sidebar .sub-list #todays-games li.individual-competitions").on("click", filterCompetitions);
  $(".sidebar .sub-list #todays-games li#all-comps-button").on("click", showAllCompetitions);
  $(".sidebar-hide-button").on("click", toggleSidebar);
});

