function login() {

    $("#loading-dialog")[0].showModal()

    const username = $("#username").val()
    const password = $("#password").val()

    fetch("/auth", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "username": username,
            "password": password
        })
    }).then((response) => {
        if(!response.ok) {
            response.text().then((text) => {
                $("#login-error").text(text)
            })
            return
        }
        $("#loading-dialog")[0].close()
        location.href = "/"
    }).catch((reason) => {
        $("#login-error").text(reason)
    })
}

$(document).ready(function() {
    $("#login").click(login)
})
