async function fetchStatus() {
    return fetchJson("/status", {
        credentials: "same-origin"
    }).catch((reason) => {
        location.href = "/login"
    })
}

function updateInterface() {
    const wan = $("#wan").attr("data-value")
    if(wan === "ethernet") {
        $(".wifi").hide()
        $(".ethernet").show()
    } else {
        $(".wifi").show()
        $(".ethernet").hide()
    }
}

function displayConnectionType(connectionType) {
    $("#wan").attr("data-value", connectionType)
    switch(connectionType) {
        case "ethernet":
            $("#wan").text("Wired")
            $("#wan").removeClass("error")
            break;
        case "wifi":
            $("#wan").text("Wireless")
            $("#wan").removeClass("error")
            break;
        default:
            $("#wan").text("Unknown")
            $("#wan").addClass("error")
            break;
    }
}

function displayInterfaceState(id, state) {
    $(id).attr("data-value", state)
    switch(state) {
        case "up":
            $(id).text("Connected")
            $(id).removeClass("error")
            $(id).addClass("success")
            break;
        case "down":
            $(id).text("Disconnected")
            $(id).addClass("error")
            $(id).removeClass("success")
            break;
        case "no-interface":
            $(id).text("Not Configured")
            $(id).addClass("error")
            $(id).removeClass("success")
            break;
        default:
            $(id).text("Unknown")
            $(id).removeClass("error")
            $(id).removeClass("success")
            break;
    }
}

$(document).ready(function() {
    fetchStatus().then((result) => {

        displayConnectionType(result.connectionType)

        displayInterfaceState("#wan-status", result.internetStatus)
        displayInterfaceState("#vpn-status", result.vpnStatus)
        displayInterfaceState("#wifi-status", result.wifiStatus)

        $("#dhcp-interfaces").text(result.dhcpInterfaces)
        
        updateInterface()
    })
});