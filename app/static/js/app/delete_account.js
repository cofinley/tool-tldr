var delete_account = (function () {

    var init = function () {
        console.log("init");
        $(".delete-account").on('click', deleteAccount);
    };

    var deleteAccount = function () {
        if (confirm("Are you sure?")) {
            if (confirm("Are you sure you're sure?")) {
                window.location.pathname = "/auth/delete-account";
            }
        }
    };

    return {
        init: init
    };
})();

$(document).ready(function () {
    delete_account.init();
});