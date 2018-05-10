var shield = (function () {

    var init = function() {
        $(".generate-shield").click(function(e){
            var $dropdownMenu = $(this);
            if ($(".shield-container").length) {
                $(".shield-url").select();
                return false;
            }
            var page_title = $(".content-page-title")
                .text()
                .replace("-", "--")
                .replace("_", "__");
            var url = generateShieldUrl(page_title);
            var html = generateShieldHtml(url);
            $dropdownMenu.after(html);

            copyShieldLinkToClipboard();
            e.stopPropagation();
        });
    };

    var copyShieldLinkToClipboard = function() {
        $(".shield-url").select();
        document.execCommand("copy");
    };

    var generateShieldUrl = function(page_title) {
        var basePath = "https://img.shields.io/badge/";
        var subject = "Tool TL;DR";
        var color = "e33b3b";
        return basePath + encodeURIComponent(subject + "-" + page_title) + "-" + color + ".svg";
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
                title: "Copied"
            })
            .tooltip({
                trigger: "click",
                placement: "right"
            })
            .on("shown.bs.tooltip", function () {
                setTimeout(function () {
                    $(".shield-link-copy-img").tooltip("hide");
                }, 2000);
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