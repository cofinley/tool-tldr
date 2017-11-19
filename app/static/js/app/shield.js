var shield = (function () {

    var init = function() {
        $(".generate-shield").click(function(e){
            var $dropdownMenu = $(this);
            if ($(".shield-container").length) {
                $(".shield-url").select();
                return false;
            }
            var pageInfo = extractPageInfoFromUrl(window.location.pathname);
            var id = pageInfo.id;
            var page_type = pageInfo.type;

            var url = generateShieldUrl(page_type, id);
            var html = generateShieldHtml(url);
            $dropdownMenu.after(html);
            copyShieldLinkToClipboard();
            e.stopPropagation();
        });
    };

    var extractPageInfoFromUrl = function(url){
        // Get page type (tool/cat) and id
        var pat = new RegExp("\\/(\\w*)\\/(\\d+)");
        var match = pat.exec(url);
        if (null !== match) {
            return {
                type: match[1],
                id: match[2]
            };
        }
    };

    var copyShieldLinkToClipboard = function() {
        $(".shield-url").select();
        document.execCommand("copy");
    };

    var generateShieldUrl = function(page_type, id) {
        var basePath = "https://img.shields.io/badge/dynamic/json.svg";
        var ttUri = window.location.origin + "/" + page_type + "/" + id + "/shield";
        var jsonKey = "name";
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

    var watchShieldDivClick = function() {
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
        watchShieldDivClick: watchShieldDivClick,
        watchClipboardCopy: watchClipboardCopy
    };
})();

$(document).ready(function () {
    shield.init();
    shield.watchShieldDivClick();
    shield.watchClipboardCopy();
});