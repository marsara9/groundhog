async function fetchStatus() {
    return fetchJson("/status", {
        credentials: "same-origin"
    }).catch((reason) => {
        location.href = "/login"
    })
}

function updateInterface() {
    const wan = $("#wan").text()
    if(wan === "ethernet") {
        $(".wifi").hide()
        $(".ethernet").show()
    } else {
        $(".wifi").show()
        $(".ethernet").hide()
    }
}

$(document).ready(function() {
    fetchStatus().then((result) => {

        switch(result.connectionType) {
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

        
        $("#wan-status").text(result.internetStatus)
        $("#vpn-status").text(result.vpnStatus)
        $("#wifi-status").text(result.wifiStatus)

        updateInterface()
    })
});