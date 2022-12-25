async function fetchInterfaces() {
    return fetchJson("/interfaces", {
        credentials: "same-origin"
    }).catch((reason) => {
        if(reason.code == 401) {
            location.href = "/login"
        }
    })
}

function updateInterface() {
    const wan = $("#wan").val()
    if(wan === "ethernet") {
        $(".wifi").hide()
        $(".ethernet").show()
    } else {
        $(".wifi").show()
        $(".ethernet").hide()
    }
    $("#ssid").val("")
    $("#passphrase").val("")
}

$(document).ready(function() {
    $("#wan").change(function() {
        updateInterface()
    })
    updateInterface()

    fetchInterfaces().then((data) => {
        // data.forEach(interface => {
        //     $("#internet-interface").append($("<option>", {
        //         value : interface,
        //         text : interface
        //     }))
        // })
    })
});