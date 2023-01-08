function submitPasswordUpdate() {
    updatePassword = getFieldData($(this))

    if($("#confirmPassword").val() != updatePassword["newPassword"]) {
        return
    }

    postJson("/user/password", updatePassword)
}

function deleteUser() {
    let dialog = $("#confirm-delete-dialog")
    $("#confirm-delete-dialog .positive").click(function() {
        dialog.hide()
        deleteJson("/user/" + getCookie("username")).then(() => {
            logout()
        })  
    })
    $("#confirm-delete-dialog .negative").click(function() {
        dialog.hide()
    })
    dialog.show()
}

$(document).ready(function() {
    $("#username").val(getCookie("username"))
    $("#submit").click(submitPasswordUpdate)
    $("#delete-user").click(deleteUser)
});
