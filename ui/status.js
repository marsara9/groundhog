async function fetchStatus() {
    return fetchJson("/status", result => {
        displayConnectionType(result.mode)

        displayInterfaceState("#wan-status", result.internetStatus)
        displayInterfaceState("#vpn-status", result.vpnStatus)
        displayInterfaceState("#wifi-status", result.wifiStatus)

        if(result.ssid != null) {
            $("#ssid").text(result.ssid)
        } else {
            $("#ssid").text("-")
        }

        if(result.securityType != null) {
            $("#security-type").text(result.securityType)
        } else {
            $("#security-type").text("-")
        }

        $("#dhcp-interfaces").text(result.dhcpInterfaces)
        
        updateInterface()
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
        case null:
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
    fetchStatus()
});