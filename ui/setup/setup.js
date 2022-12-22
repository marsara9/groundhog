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
});