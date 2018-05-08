var tooltip_engine = (function(){

    var cache = {};
    var tooltipUrlPrefix = "/tip/";
    var selector = "/categories/";
    var excludedSubRoutes = ["edit", "edits", "add-new-tool"];

    var categoryInfoLookup = function(categoryId, success) {
        $.ajax({
            url: tooltipUrlPrefix + categoryId,
            async: false,
            dataType: "text",
            success: success
        });
    };

    var loadCategoryInfo = function() {
        // Only look for links like '/categories/15', nothing else.

        if (typeof $(this).data("notitle") !== 'undefined') {
            // Skip tooltip when explicitly disabled
            return false;
        }

        var route = $(this).attr('href');
        var idPattern = new RegExp("^\\/categories\\/(\\d+)\\/([a-z0-9-]*)$");
        var categoryIdMatch = idPattern.exec(route);

        if ((null !== categoryIdMatch) && ($.inArray(categoryIdMatch[2], excludedSubRoutes) === -1)){

            var categoryId = categoryIdMatch[1];
            if (!cache.hasOwnProperty(categoryId)) {
                categoryInfoLookup(categoryId, function(result) {
                    cache[categoryId] = result;
                });
            }
            return cache[categoryId];
        }
    };

    var init = function() {
        $("body").tooltip({
            selector: 'a[href^="' + selector + '"]',
            placement: 'auto',
            trigger: 'hover',
            delay: 400,
            title: loadCategoryInfo,
            html: true,
            template: '<div class="tooltip" role="tooltip"><div class="arrow"></div><div class="tooltip-inner text-left"></div></div>'
        })
            .on("show.bs.tooltip", function () {
                // Fix bug on explore, only allow one tooltip instance visible at a time
                // Remove all when tooltip about to be shown
                $(".tooltip").remove();
            });
    };

    return {
        init: init
    };
})();

$(document).ready(function() {
    tooltip_engine.init();
});