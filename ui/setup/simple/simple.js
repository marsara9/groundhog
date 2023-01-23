function fetchConfiguration() {
    fetchJson("/simple/configuration", result => {
        genericPopulateFields(result)

        const update = updateMode.bind($("#mode"))
        update()
    })
}

function submitConfiguration() {
    const data = {
        ...getFieldData($("#mode")),
        ...getFieldData($("#wifi-ssid")),
        ...getFieldData($("#vpn-url"))
    }

    let url = $("#vpn-url").val()
    let port = $("#vpn-port").val()
    data["vpn"]["endpoint"] = `${url}:${port}`

    console.log(data)

    putJson("/simple/configuration", data, () => {
        $("#config-update-response").addClass("success")
            .removeClass("error")
            .text("Configuration Updated")
    }, reason => {
        $("#config-update-response").removeClass("success")
            .addClass("error")
            .text(reason.message)
    })
}

function parseConfigFile() {
    const reader = new FileReader()
    reader.addEventListener("load", (event) => {
        const contents = event.target.result
        
        const data = contents.split("\n").filter(line => {
            return line.includes("=")
        }).map(line => {
            const values = line.split("=")
            return values.map(it => {
                return it.trim()
            })
        })
        
        var result = {}
        data.forEach(it => {
            result[it[0].toLowerCase()] = it[1]
        })
        
        setConfiguration(result)
    })
    const file = $(this).prop("files")[0]
    if(file) {
        reader.readAsText(file)
    }
}

function setConfiguration(configuration) {
    const url = configuration.endpoint.split(":")[0]
    const port = configuration.endpoint.split(":")[1]
    const dns = configuration.dns.split(",")

    const vpnAllowedIPs = configuration.allowedips.split(",")

    $("#vpn-url").val(url)
    $("#vpn-port").val(port)
    $("#vpn-subnet").val(vpnAllowedIPs[0])

    $("#vpn-keys-private").val(configuration.privatekey)
    $("#vpn-keys-public").val(configuration.publickey)
    $("#vpn-keys-preshared").val(configuration.presharedkey)

    $("#vpn-address").val(configuration.address)
    $("#dhcp-dns-0").val(dns[0])
    $("#dhcp-dns-1").val(dns[1])
}

function scanWiFi() {
    const dialog = $("#wifi-scan-dialog")
    const status = dialog.find("#wifi-scan-status")
    const scanResults =  dialog.find("#wifi-scan-results")

    status.show()
    scanResults.hide()
    scanResults.empty()
    
    fetchJson("/wifi/scan", results => {

        resultsArray = []
        for(ssid in results) {
            resultsArray.push(results[ssid])
            resultsArray[resultsArray.length - 1]["name"] = ssid
        }

        resultsArray.sort(function(lhs, rhs) {
            return rhs.strength - lhs.strength
        })

        for(let i = 0; i < resultsArray.length; i++) {
            const result = resultsArray[i]

            let signalStrengthFactor = Math.ceil(result.strength / 20)

            const signalName = $("<span></span>")
                .text(result.name)
            const signalStrengthImg = $("<img></img>")
                .attr("src", `/imgs/wifi/wifi-${signalStrengthFactor}.svg`)
                .attr("height", 24)
            const item = $("<li></li>")
                .append(signalName)
                .append(signalStrengthImg)
                .click(function() {
                    item.siblings("li.active").removeClass("active")
                    item.addClass("active")
                    
                    dialog.find("button.positive").prop("disabled", false)
                })
            scanResults.append(item)
        }

        status.hide()
        scanResults.show()

        $("#wifi-refresh > img").attr("src", "/imgs/reload/reload-static.svg")

    }, reason => {
        status.text(reason.message)
    })
    
    if(!dialog.attr("open")) {
        dialog[0].showModal()
    }
    dialog.find("button.positive").click(function() {
        const value = dialog.find("li.active").text()
        $("#wifi-ssid").val(value)
    })
}

function refreshWiFi(e) {
    e.preventDefault()

    $("#wifi-refresh > img").attr("src", "/imgs/reload/reload-animated.svg")

    scanWiFi()
}

function updateMode() {
    $(".wifi,.ethernet").hide()
    const id = $(this).val()
    $(`.${id}`).show()
}

$(document).ready(function() {
    fixAutofill([
        "wifi-ssid", 
        "wifi-passphrase"
    ])

    fetchConfiguration()
    $("#file").on("change", parseConfigFile)
    $("#mode").on("change", updateMode)
    $("#submit").click(submitConfiguration)
    $("#wifi-scan").click(scanWiFi)
    $("#wifi-refresh").click(refreshWiFi)
});
