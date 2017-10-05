var maxLength = 250;

function watchTextArea(textAreaId) {
    var charCountId = textAreaId + "-count";
    if ($(textAreaId).length) {
        if ($(textAreaId).val().length > 0) {
            var charsLeft = maxLength - $(textAreaId).val().length;
            $(charCountId).text(charsLeft);
        }
    }
    $(textAreaId).keyup(function () {
        var charsLeft = maxLength - $(this).val().length;
        $(charCountId).text(charsLeft);
    });
}

$(document).ready(function(){
    $("#what").ready(function() {
        watchTextArea("#what");
    });
    $("#where").ready(function() {
        watchTextArea("#where");
    });
    $("#why").ready(function() {
        watchTextArea("#why");
    });
});
