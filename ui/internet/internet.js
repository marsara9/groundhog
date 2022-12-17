async function fetchInterfaces(callback) {
    return fetchJson("/interfaces")
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
