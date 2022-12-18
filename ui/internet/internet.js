async function fetchInterfaces() {
    return fetchJson("/interfaces", {
        credentials: "same-origin"
    }).catch((reason) => {
        //location.href = "/login"
    })
}

$(document).ready(function() {
    fetchInterfaces().then((data) => {
        data.forEach(interface => {
            $("#internet-interface").append($("<option>", {
                value : interface,
                text : interface
            }))
        })
    })
})
