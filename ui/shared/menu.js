$(document).ready(function() {
    $("#logout").click(logout)

    $("#profile").text(getCookie("username"))
});
