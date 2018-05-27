var explore = (function () {

    var generalTreeSelector = ".explore-tree";
    var exploreTreeSelector = ".explore-tree-explore";
    var editTreeSelector = ".explore-tree-edit";
    var exploreTree = {
        selector: ".explore-tree-explore",
        opts: {
            "show_root": false,
            "show_links": true
        }
    };
    var editTreeCategory = {
        selector: ".explore-tree-edit-category",
        opts: {
            "show_root": true,
            "show_links": false,
            "only_categories": true
        }
    };
    var editTreeTool = {
        selector: ".explore-tree-edit-tool",
        opts: {
            "show_root": false,
            "show_links": false,
            "only_categories": true
        }
    };
    var trees = [exploreTree, editTreeCategory, editTreeTool];

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
                    if (-1 !== node.id) {
                        populateFormField(node);
                    }
                }
            })
            .bind('tree.init', function () {
                // Auto-open root node if it's present
                var node = $(this).tree('getNodeById', 0);
                $(this).tree('openNode', node);
            });

        $('#collapse-button').click(collapseTree);

        $("#filter-tree").on("input", filterTree);
    };

    var filterTree = function () {
        var query = $(this).val();
        var params = {"q": query};
        var currentTree;
        for (var t in trees) {
            if ($(trees[t].selector).length) {
                currentTree = trees[t];
            }
        }
        $.extend(params, currentTree.opts);

        var currentURL = new URL(window.location.href);
        var currentParams = {};
        var available_params = ["id", "envs"];
        $.each(available_params, function (i, param) {
            var value = currentURL.searchParams.get(param);
            if (null !== value) {
                if ("id" === param) {
                    param = "ceiling";
                }
                currentParams[param] = value;
            }
        });
        $.extend(params, currentParams);

        var filterURL = window.location.origin + "/filter_nodes?" + $.param(params);
        $(currentTree.selector).tree("loadDataFromUrl", filterURL, null, function () {
            var rootTree = $(currentTree.selector).tree("getTree");
            // Open root by default
            var root = $(currentTree.selector).tree('getNodeById', 0);
            $(currentTree.selector).tree('openNode', root);
            // Expand all nodes if filtered tree
            if (query.length) {
                rootTree.iterate(function (node) {
                    if (!node.load_on_demand) {
                        // Only auto-open if no load_on_demand (forces folder icon)
                        // Used for category endpoints on query
                        $(currentTree.selector).tree("openNode", node);
                        return true;
                    }
                });
            }
        });
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