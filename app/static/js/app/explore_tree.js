$('#explore-tree').tree({
    dragAndDrop: false,
    openedIcon: $('<span class="openedIcon toggler"></span>'),
    closedIcon: $('<span class="closedIcon toggler"></span>'),
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


function populateFormField(node) {
    console.log("populating...");
    if ($("#parent_category")) {
        $("#parent_category").attr("value", node.name);
        $("#parent_category_id").attr("value", node.id);
    }
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

            populateFormField(node);

            if (previousNodeClicked) {
                var prev;
                prev = $tree.tree('getNodeById', previousNodeClicked);
                if (previousNodeClicked !== node.id) {
                    // Clicked on different id after the previous one, hide previous
                    $(prev.element).find(".blurb").first().hide();
                }
                else {
                    // Same id clicked, keep showing
                    $(prev.element).find(".blurb").first().show();
                }
            }

            previousNodeClicked = node.id;

            // Find element count, if less than two, that means blurb hasn't been created yet
            var count = $($row).find("span").length;

            if (count < 2) {
                // Blurb element not yet created
                var blurb = getBlurb(node.id);
                var span = document.createElement("span");
                span.className = "blurb";
                span.textContent = blurb;
                $(span).attr("title", blurb);
                $(span).appendTo($row);
            }
            else {
                // Blurb already there, just hidden
                $($($row).children()[2]).show();
            }
        }
        else {
            // event.node is null
            // a node was deselected
            // e.previous_node contains the deselected node
            // Hide blurb if deselected
            $(event.previous_node.element).find(".blurb").first().hide();
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

