var maxLength = 250;

function watchTextArea(textAreaId) {
    var charCountId = textAreaId + "-count";
    $(textAreaId).keyup(function () {
        var charsLeft = maxLength - $(this).val().length;
        $(charCountId).text(charsLeft);
    });
}

$(document).ready(function(){
    watchTextArea("#what");
    watchTextArea("#why");
    watchTextArea("#where");
});
