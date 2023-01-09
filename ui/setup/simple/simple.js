function fetchConfiguration() {
    fetchJson("/dhcp/configuration", result => {
        genericPopulateFields(result)
    })
}

function submitConfiguration() {
    const data = {
        ...getFieldData($("#subnet")),
        ...getFieldData($("ssid")),
        ...getFieldData($("#vpn-endpoint"))
    }

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
    const wanIp = configuration.address.split("/")[0]

    $("#vpn-url").val(url)
    $("#vpn-port").val(port)
    $("#vpn-endpoint").val(configuration.endpoint)

    $("#private-key").val(configuration.privatekey)
    $("#public-key").val(configuration.publickey)
    $("#preshared-key").val(configuration.presharedkey)

    $("#wan-ip").val(wanIp)
    $("#dns-0").val(dns[0])
    $("#dns-1").val(dns[1])
}

$(document).ready(function() {

    $("#vpn-url").on("input", function() {
        $("#vpn-endpoint").val($(this).val() + ":" + $("#vpn-port").val())
    })
    $("#vpn-port").on("input", function() {
        $("#vpn-endpoint").val($("#vpn-url").val() + ":" + $(this).val())
    })

    fetchConfiguration()
    $("#file").on("change", parseConfigFile)
    $("#submit").click(submitConfiguration)
});
