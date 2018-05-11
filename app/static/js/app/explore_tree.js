var explore = (function () {

    var generalTreeSelector = ".explore-tree";
    var exploreTreeSelector = ".explore-tree-explore";
    var editTreeSelector = ".explore-tree-edit";

    var treeOptions = {
        dragAndDrop: false,
        openedIcon: $('<span class="opened-icon toggler"></span>'),
        closedIcon: $('<span class="closed-icon toggler"></span>'),
        useContextMenu: false,
        autoEscape: false,
        selectable: false
    };

    var init = function () {
        $(exploreTreeSelector).tree(treeOptions);

        $(editTreeSelector)
            .tree($.extend(true, treeOptions, {selectable: true}))
            .bind('tree.select', function (event) {
                if (event.node) {
                    // node was selected
                    var node = event.node;
                    populateFormField(node);
                }
            })
            .bind('tree.init', function () {
                // Auto-open root node if it's present
                var node = $(this).tree('getNodeById', 0);
                $(this).tree('openNode', node);
            });

        $('#collapse-button').click(collapseTree);
    };

    var collapseTree = function () {
        $(this).blur();
        var $tree = $(generalTreeSelector);
        $tree.tree('getTree')
            .iterate(function (node) {
                if (node.hasChildren()) {
                    $tree.tree('closeNode', node, true);
                }
                return true;
            });
    };

    var populateFormField = function (node) {
        if ($("#parent_category")) {
            $("#parent_category").attr("value", node.name);
            $("#parent_category_id").attr("value", node.id);
        }
    };

    return {
        init: init
    };

})();

$(document).ready(function () {
    explore.init();
});