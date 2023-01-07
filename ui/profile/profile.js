
function getPasswordUpdate(submit) {
    updatePassword = {}
    submit.parents("dl.prop-grid").find("input:not(.ignore)").each(function() {
        const input = $(this)        
        updatePassword[input.attr("id")] = input.val()
    })

    return updatePassword
}

function submitPasswordUpdate() {
    updatePassword = getPasswordUpdate($(this))

    if($("#confirmPassword").val() != updatePassword["newPassword"]) {
        return
    }

    postJson("/user/password", updatePassword)
}

$(document).ready(function() {
    $("#username").val(getCookie("username"))
    $("#submit").click(submitPasswordUpdate)
});
