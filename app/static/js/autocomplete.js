$(function () {
    var cache = {};
    $("#search-input").autocomplete({
        minLength: 3,
        classes: {
            "ui-autocomplete": "autocomplete-highlight autocomplete-small"
        },
        source: function (request, response) {
            console.table(request);
            var term = request.term;
            if (term in cache) {
                response(cache[term]);
                return;
            }

            $.getJSON(window.location.origin + "/search", request, function (data, status, xhr) {
                console.log("term: " + term);
                console.log("data: " + data);
                cache[term] = data;
                response(data);
            });
        },
        select: function (event, ui) {
            event.preventDefault();
            window.location.href = window.location.origin + "/tools/" + ui.item.value;
            return false;
        }
    });
    $("#big-search-bar-input").autocomplete({
        minLength: 3,
        classes: {
            "ui-autocomplete": "autocomplete-highlight autocomplete-big"
        },
        source: function (request, response) {
            var term = request.term;
            if (term in cache) {
                response(cache[term]);
                return;
            }

            $.getJSON(window.location.origin + "/search", request, function (data, status, xhr) {
                cache[term] = data;
                response(data);
            });
        },
        select: function (event, ui) {
            event.preventDefault();
            window.location.href = window.location.origin + "/tools/" + ui.item.value;
            return false;
        }
    });
});