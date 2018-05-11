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

var $tree = $(generalTreeSelector);

$('#collapse-button').click(function() {
    $(this).blur();
    var tree = $tree.tree('getTree');
    tree.iterate(function (node) {

        if (node.hasChildren()) {
            $tree.tree('closeNode', node, true);
        }
        return true;
    });
});

function populateFormField(node) {
    if ($("#parent_category")) {
        $("#parent_category").attr("value", node.name);
        $("#parent_category_id").attr("value", node.id);
    }
}

