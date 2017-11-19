var shield = (function () {

    // TODO: make shields work on tools (pick out of url in extract, keep as global var to reference in other functions)

    var init = function() {
        $(".generate-shield").click(function(e){
            var $dropdownMenu = $(this);
            if ($(".shield-container").length) {
                $(".shield-url").select();
                return false;
            }
            var id = extractCategoryIdFromUrl(window.location.pathname);
            var url = generateShieldUrl(id);
            var html = generateShieldHtml(url);
            $dropdownMenu.after(html);
            copyShieldLinkToClipboard();
            e.stopPropagation();
        });
    };

    var extractCategoryIdFromUrl = function(url){
        var idPattern = new RegExp("\\/categories\\/(\\d+)");
        var match = idPattern.exec(url);
        if (null !== match) {
            return match[1];
        }
    };

    var copyShieldLinkToClipboard = function() {
        $(".shield-url").select();
        document.execCommand("copy");
    };

    var generateShieldUrl = function(id) {
        var basePath = "https://img.shields.io/badge/dynamic/json.svg";
        var ttUri = "https://tooltldr.com/categories/" + id + "/shield";
        var jsonKey = "c";
        var data = {
            label: "Tool TL;DR",
            colorB: "e33b3b",
            query: jsonKey,
            uri: ttUri
        };
        var paramData = $.param(data);
        return basePath + "?" + paramData;
    };

    var generateShieldHtml = function(url) {
        var $shieldDiv = $("<div/>").addClass("shield-container");

        var $hr = $("<hr>");
        var $shieldImageRow = $("<img/>")
            .addClass("shield-img")
            .attr("src", url);

        var $shieldLinkRow = $("<div/>")
            .addClass("d-flex justify-content-around align-items-center shield-link-row");
        var $shieldLink = $("<input/>")
            .addClass("shield-url")
            .attr("type", "text")
            .val(url);
        var $copyClipboardSvg = $("<img/>")
            .addClass("shield-link-copy-img")
            .attr({
                src: "/static/img/copyclip.svg",
                title: "Copy link to clipboard"
            });
        $shieldLinkRow.append([$shieldLink, $copyClipboardSvg]);

        $shieldDiv.append([$hr, $shieldImageRow, $shieldLinkRow]);
        return $shieldDiv;
    };

    var watchShieldDiv = function() {
        // Don't allow dropdown to close when clicking on shield or other shield-related elements
        $(".dropdown-menu").on('click', ".shield-container", function (e) {
            e.stopPropagation();
        });
    };

    var watchClipboardCopy = function() {
        $(".dropdown-menu").on('click', ".shield-link-copy-img", function (e) {
            copyShieldLinkToClipboard();
        });
    };

    return {
        init: init,
        watchShieldDiv: watchShieldDiv,
        watchClipboardCopy: watchClipboardCopy
    };
})();

$(document).ready(function () {
    shield.init();
    shield.watchShieldDiv();
    shield.watchClipboardCopy();
});