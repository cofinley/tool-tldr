$(".cancel-button").click(function() {
    window.history.back();
});

function navigateFromAutocomplete(dataset) {
    var id = dataset.id;
    if (id === "-1") {
        return false;
    }
    var type = dataset.type === 't' ? 'tools' : 'categories';
    window.location.href = window.location.origin + "/" + type + "/" + id;
}

$("#search-input").keyup(function(event) {
    if ($(".autocomplete-suggestion.selected").length > 0) {
        if (event.keyCode === 13) {
            var dataset = $(".autocomplete-suggestion.selected")[0].dataset;
            navigateFromAutocomplete(dataset);
        }
    }
});

$("#big-search-bar-input").keyup(function (event) {
    if ($(".autocomplete-suggestion-big.selected").length > 0) {
        if (event.keyCode === 13) {
            var dataset = $(".autocomplete-suggestion-big.selected")[0].dataset;
            navigateFromAutocomplete(dataset);
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

$.each($(".form-control-label"), function (i, label) {
    var text = $(label).text();
    if (text.includes("*")) {
        var html = $(label).html();
        var redAsterisk = $("<span>*</span>").addClass("red-text");
        $(label).html(html.replace("*", redAsterisk.get(0).outerHTML));
    }
});
