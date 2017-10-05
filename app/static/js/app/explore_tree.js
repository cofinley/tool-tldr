$('#explore-tree').tree({
    dragAndDrop: false,
    openedIcon: $('<span class="opened-icon toggler"></span>'),
    closedIcon: $('<span class="closed-icon toggler"></span>'),
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

function getBlurbJson(node, callback){
    var rdata = {id: node.id};
    if (node.env) {
        rdata.tool = true;
    }
    $.getJSON("/load_blurb", rdata, function (data) {
    }).done(function(data){
        callback(data);
    });
}

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
            var elem = node.element;
            var row = $(elem).find("div")[0];

            populateFormField(node);
            // Reset state
            $(".blurb").hide();
            $("li.jqtree_common").not($(elem)).removeClass("jqtree-selected");

            var count =$(row).find(".blurb").length;
            if ((count === 0) && (node.id !== 0)){
                var span = document.createElement("span");
                getBlurbJson(node, function(data){
                    span.textContent = data.blurb;
                    $(span).attr("title", data.blurb);
                });
                span.className = "blurb";
                $(span).appendTo(row);
            }
            else {
                $($(row).find(".blurb")[0]).show();
            }
        }
        else {
            $(".blurb").hide();
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
