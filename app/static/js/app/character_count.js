var characterCount = (function() {
    var fieldLength = 250;

    var watchTextArea = function(textAreaId, max) {
        var maxLength = max || fieldLength;
        $(textAreaId).ready(function(){
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
        });
    };

    return {
        init: watchTextArea
    };
})();

$(document).ready(function(){
    characterCount.init("#what");
    characterCount.init("#where");
    characterCount.init("#why");
    characterCount.init("#edit_msg", 100);
    characterCount.init("#body", 500);
});
