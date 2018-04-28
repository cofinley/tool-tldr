var comments = (function () {

    var init = function () {
        $(".comment-delete").on("click", deleteComment);
    };

    var deleteComment = function (e) {
        if (!confirm("Are you sure you want to delete this comment?")) {
            return false;
        }
    };

    return {
        init: init
    };
})();

$(document).ready(function () {
    comments.init();
});