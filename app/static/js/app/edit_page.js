$("#move_parent").change(function(){
    $("#tree-pane, #optional_parent_field").toggleClass("initially-hidden-field");
});

// Set max date created year
var today = new Date();
var year = today.getFullYear();

$("input#created").attr("max", year);