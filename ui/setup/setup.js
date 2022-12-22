async function fetchInterfaces() {
    return fetchJson("/interfaces", {
        credentials: "same-origin"
    }).catch((reason) => {
        location.href = "/login"
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

function setupTabs() {
    $(".tabbar").each(function() {
        const tabs = $(this).children("button.tab")
        tabs.each(function() {
            $($(this).attr("data-content")).hide()
            $(this).click(function() {
                tabs.each(function() {
                    $(this).removeClass("selected")
                    $($(this).attr("data-content")).hide()
                })

                $(this).addClass("selected")
                $($(this).attr("data-content")).show()
            })
        })
        tabs.first().click()
    })
}

$(document).ready(function() {
    setupTabs()

    $("#wan").change(function() {
        updateInterface()
    })
    updateInterface()

    // fetchInterfaces().then((data) => {
    //     data.forEach(interface => {
    //         $("#internet-interface").append($("<option>", {
    //             value : interface,
    //             text : interface
    //         }))
    //     })
    // })
});