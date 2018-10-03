var softlinks = (function () {

    var init = function () {
        var textareas = ".sl";

        $(textareas).atwho({
            at: "!",
            startWithSpace: false,
            displayTpl: "<li><span class='atwho-small-text'>${type} #${id}</span>${label}</li>",
            insertTpl: "${atwho-at}${type}-${id}",
            data: null,
            searchKey: "label",
            callbacks: {
                filter: function (q, data, searchKey) {
                    if (null === q || q.length < 1) {
                        return [];
                    }
                },
                remoteFilter: function(q, cb) {
                    if (null === q || q.length < 1) {
                        return cb([]);
                    }
                    $.get(window.location.origin + "/search", {q: q, e: true}, function (data) {
                        cb(data.map(function(currentValue, idx, arr){
                            currentValue.type = currentValue.type === "c" ? "Category" : "Tool";
                            return currentValue;
                        }));
                    });
                }
            }
        });
    };

    return {
        init: init
    };
})();

$(document).ready(function () {
    softlinks.init();
});
