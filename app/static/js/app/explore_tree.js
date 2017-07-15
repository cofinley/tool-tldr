$('#explore-tree').tree({
    dragAndDrop: false,
    closedIcon: '+',
    openedIcon: '-',
    useContextMenu: false,
    autoEscape: false,
    selectable: true
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

var cachedNodes = {};

function getBlurb(id) {
    // If node id not in cachedNodes, getJson, else do lookup
    var blurb;
    if (cachedNodes.hasOwnProperty(id)) {
        blurb = cachedNodes[id];
    }
    else {
        $.ajax({
          dataType: "json",
          url: "/load_blurb",
          data: {id: id},
          async: false
        })
            .done(function(response) {
                blurb = response.blurb;
                cachedNodes[id] = blurb;
            });
    }
    return blurb;
}

var previousNodeClicked;

$tree.bind(
    'tree.select',
    function(event) {
        if (event.node) {
            // node was selected
            var node = event.node;
            var elem = node.element;
            var $row = $(elem).find("div")[0];

            if (previousNodeClicked) {
                if (previousNodeClicked !== node.id) {
                    var prev = $tree.tree('getNodeById', previousNodeClicked);
                    $(prev.element).find(".blurb").css("display", "none");
                }
            }

            previousNodeClicked = node.id;

            var count = $($row).find("span").length;

            if (count < 2) {
                var blurb = getBlurb(node.id);
                var span = document.createElement("span");
                span.className = "blurb";
                span.textContent = blurb;
                $(span).css("display", "initial");
                $(span).attr("title", blurb);
                $(span).appendTo($row);
            }
            else {
                $($($row).children()[2]).css("display", "initial");
            }
        }
        else {
            // event.node is null
            // a node was deselected
            // e.previous_node contains the deselected node
            // $(event.previous_node.element).find(".blurb").css("display", "none");
        }
    }
);