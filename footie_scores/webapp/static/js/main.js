function showSubList () {

}

$( document ).ready(function() {
  $(".sidebar strong").on("click", function(){
    $(this).next().children(".sub-list").toggle();
  })
  
});

