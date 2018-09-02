var autocomplete = (function () {

    var init = function (selector) {
        var bigSize = selector === "#big-search-bar-input";
        var loaderDiv = bigSize ? '#big-loader' : '#small-loader';

        var xhr;
        new autoComplete({
            selector: selector,
            minChars: 1,
            source: function (term, response) {
                $(loaderDiv).show();
                try {
                    xhr.abort();
                } catch (e) {
                }
                xhr = $.getJSON(window.location.origin + '/search', {q: term}, function (data) {
                    $(loaderDiv).hide();
                    response(data);
                });
            },
            renderItem: function (item, search) {
                var obj = item;
                item = obj.label;
                search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");

                var className = 'autocomplete-suggestion';
                if (bigSize) {
                    className += ' autocomplete-suggestion-big';
                }

                var suggestionDiv = document.createElement('div');
                suggestionDiv.setAttribute('class', className);
                suggestionDiv.setAttribute('data-id', obj.id);
                suggestionDiv.setAttribute('data-type', obj.type);
                suggestionDiv.setAttribute('data-val', obj.label);
                suggestionDiv.innerHTML = item.replace(re, "<b>$1</b>");

                return suggestionDiv.outerHTML;
            },
            onSelect: function (e, term, item) {
                // Handles clicks, enter key is handled by utils.js keyup handlers
                // Still need to handle all types here to take care of clicks
                if (e.keyCode === 13) {
                    e.preventDefault();
                }
                var itemData = item.dataset;
                if (itemData.type === '0') {
                    return false;
                }
                else if (itemData.type === 't') {
                    window.location.href = window.location.origin + '/tools/' + itemData.id;
                }
                else if (itemData.type === 'c') {
                    window.location.href = window.location.origin + '/categories/' + itemData.id;
                }
            }
        });
    };
    return {
        init: init
    };
})();

$(document).ready(function () {
    if ($("#big-search-bar-input").is(":visible")) {
        autocomplete.init("#big-search-bar-input");
    }
    if ($("#search-input").is(":visible")) {
        autocomplete.init("#search-input");
    }
    if ($("#mobile-search-input").is(":visible")) {
        autocomplete.init("#mobile-search-input");
    }
});
