var environments = (function () {

    var init = function () {
        var environmentFormField = "input#environments";

        $(environmentFormField).selectize({
            preload: "focus",
            persist: false,
            create: function (input) {
                return {
                    value: input.toLowerCase(),
                    label: input.toLowerCase()
                };
            },
            load: function (query, callback) {
                if (!query.length) return callback();
                $.get(window.location.origin + "/search-envs", {q: query}, function (data) {
                    callback(data);
                });
            },
            valueField: "label",
            labelField: "label",
            searchField: "label",
            onInitialize: function () {
                $(".selectize-control").removeClass("form-control");
            },
            render: {
                item: function (data, escape) {
                    var field_label = this.settings.labelField;
                    return '<div class="item tool-environment">' + escape(data[field_label]) + '</div>';
                }
            }
        });
    };

    return {
        init: init
    };
})();

$(document).ready(function () {
    environments.init();
});