function submitPasswordUpdate() {
    updatePassword = getFieldData($(this))

    if($("#confirm-password").val() != updatePassword["new-password"]) {
        $("#confirm-password").addClass("error")
        return
    }

    $("#confirm-password").removeClass("error")

    postJson("/user/password", updatePassword, 
        onResult = () => {
            $("#change-password-response").addClass("success")
            $("#change-password-response").removeClass("error")
            $("#change-password-response").text("Password Updated")
        },
        onError = reason => {
            $("#change-password-response").removeClass("success")
            $("#change-password-response").addClass("error")
            $("#change-password-response").text(reason.message)
        }
    )
}

function deleteUser() {
    let dialog = $("#confirm-delete-dialog")[0]
    $("#confirm-delete-dialog .positive").click(function() {
        dialog.close()
        deleteJson("/user/" + getCookie("username")).then(() => {
            logout()
        })  
    })
    $("#confirm-delete-dialog .negative").click(function() {
        dialog.close()
    })
    dialog.showModal()
}

$(document).ready(function() {
    $("#username").val(getCookie("username"))
    $("#submit").click(submitPasswordUpdate)
    $("#delete-user").click(deleteUser)
});
