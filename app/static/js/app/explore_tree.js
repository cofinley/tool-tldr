$('#explore-tree').tree({
    dragAndDrop: false,
    closedIcon: '+',
    openedIcon: '-',
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