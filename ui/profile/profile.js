function submitPasswordUpdate() {
    updatePassword = getFieldData($(this))

    if($("#confirmPassword").val() != updatePassword["newPassword"]) {
        return
    }

    postJson("/user/password", updatePassword)
}

$(document).ready(function() {
    $("#username").val(getCookie("username"))
    $("#submit").click(submitPasswordUpdate)
});
