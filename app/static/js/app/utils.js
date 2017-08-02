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


$("#search-input").keyup(function(event) {
    if ($(".autocomplete-suggestion.selected").length > 0) {
        if (event.keyCode === 13) {
            var dataset = $(".autocomplete-suggestion.selected")[0].dataset;
            var id = dataset.id;
            var type = dataset.type === 't' ? 'tools' : 'categories';
            window.location.href = window.location.origin + "/" + type + "/" + id;
        }
    }
});

$("#big-search-bar-input").keyup(function (event) {
    if ($(".autocomplete-suggestion-big.selected").length > 0) {
        if (event.keyCode === 13) {
            var dataset = $(".autocomplete-suggestion-big.selected")[0].dataset;
            var id = dataset.id;
            var type = dataset.type === 't' ? 'tools' : 'categories';
            window.location.href = window.location.origin + "/" + type + "/" + id;
        }
    }
});