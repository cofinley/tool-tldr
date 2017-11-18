$('#explore-tree').tree({
    dragAndDrop: false,
    openedIcon: $('<span class="opened-icon toggler"></span>'),
    closedIcon: $('<span class="closed-icon toggler"></span>'),
    useContextMenu: false,
    autoEscape: false,
    selectable: false
});

var $tree = $('#explore-tree');
$('#collapse-button').click(function() {
  $(this).blur();
  var tree = $tree.tree('getTree');
  tree.iterate(function(node) {

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

$tree.bind(
    'tree.select',
    function (event) {
        if (event.node) {
            // node was selected
            var node = event.node;
            populateFormField(node);
        }
    }
);

$tree.bind(
    'tree.init',
    function () {
        // Auto-open root node if it's present
        var node = $tree.tree('getNodeById', 0);
        $tree.tree('openNode', node);
    }
);
