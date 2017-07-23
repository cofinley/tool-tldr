function goBack() {
    window.history.back();
}

$(".add-button").hover(function(){
   // Show dropdown on add button hover
   $(".dropdown-menu").show();

   // After one second of initial add button hover, make sure mouse not over dropdown menu elements
   setInterval(function () {
       if ($('.dropdown:hover, .dropdown-menu:hover').length === 0) {
           $(".dropdown-menu").hide();
       }
   }, 1000);
});