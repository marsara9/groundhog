async function fetchInterfaces(callback) {
    return fetchJson("/interfaces")
}

function load() {
    fetchInterfaces().then((data) => {
        data.forEach(interface => {
            $("#internet-interface").append($("<option>", {
                value : interface,
                text : interface
            }))
        })
    })
}

$(document).ready(function() {
    load()
})
