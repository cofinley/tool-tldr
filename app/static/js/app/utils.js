$(".cancel-button").click(function() {
    window.history.back();
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

$("#hamburguesa img").click(function(){
    $("#nav-menu-arrow-up").toggle();
    $("#nav-menu").toggle();
});

$("#show-add-options").click(function(){
    var amount = screen.width < 576 ? 180 : 200;
    $("#nav-menu-pages").animate({
        right: '+=' + amount + 'px'
    });
});

$("#hide-add-options").click(function () {
    var amount = screen.width < 576 ? -180 : -200;
    $("#nav-menu-pages").animate({
        right: '+=' + amount + 'px'
    });
});

$(".search-form").on({
    'focus': function() {
        this.placeholder = '';
    },
    'blur': function() {
        this.placeholder = this.id.includes('big') ? 'Search software tools' : 'Search';
    }
});

// Saving for rainy day...
function extractPageInfoFromUrl(url) {
    // Get page type (tool/cat) and id
    var pat = new RegExp("\\/(\\w*)\\/(\\d+)");
    var match = pat.exec(url);
    if (null !== match) {
        return {
            type: match[1],
            id: match[2]
        };
    }
}
