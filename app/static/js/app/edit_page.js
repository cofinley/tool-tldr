$("#move_parent").change(function(){
    $(".initially-hidden-field").toggle();
    $("#tree-pane").toggle();
});

$("#edit_avatar_url").change(function(){
    $("#avatar-url-field").toggle();
});

$("#edit_link").change(function(){
    $("#project-url-field").toggle();
});

$("#edit_link, #edit_avatar_url").change(function(){

    // Show recaptcha if one or more link fields are being changed

    if ($("#edit_link, #edit_avatar_url").is(":checked")) {
        // one or more checked
        $("#edit-tool-recaptcha").show();
    }
    else {
        // nothing checked
        $("#edit-tool-recaptcha").hide();
    }
});

var today = new Date();
var year = today.getFullYear();

$("input#created").attr("max", year);