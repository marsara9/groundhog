function fetchConfiguration() {
    fetchJson("/simple/configuration", result => {
        genericPopulateFields(result)

        console.log(result)

        //const localIpAddress = result["lanip"]
        //const netmask = localIpAddress.split("/")[1]

        switch(result.mode) {
            case "wifi", "unknown":
                $(".wifi").show()
                $(".ethernet").hide()
                break;
            case "ethernet":
                $(".wifi").hide()
                $(".ethernet").show()
                break;
            default:
                $(".wifi").hide()
                $(".ethernet").hide()
                break;
        }

        //$("#lanip").val(localIpAddress.split("/")[0])
        //$("#subnet").text(`${getSubnet(localIpAddress)}/${netmask}`)
    })
}

function submitConfiguration() {
    const data = {
        ...getFieldData($("#subnet")),
        ...getFieldData($("#wifi-ssid")),
        ...getFieldData($("#vpn-url"))
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

    const vpnAllowedIPs = configuration.allowedips.split(",")

    $("#vpn-url").val(url)
    $("#vpn-port").val(port)
    $("#vpn-subnet").val(vpnAllowedIPs[0])

    $("#vpn-keys-private").val(configuration.privatekey)
    $("#vpn-keys-public").val(configuration.publickey)
    $("#vpn-keys-preshared").val(configuration.presharedkey)

    $("#wan-ip").val(wanIp)
    $("#vpn-dns-0").val(dns[0])
    $("#vpn-dns-1").val(dns[1])
}

function ipToint(ipAddress) {
    return ipAddress.split('.')
      .reduce(function(ipInt, octet) { 
        return (ipInt<<0x08) + parseInt(octet, 10)
      }, 0) >>> 0
  }
  
function intToip (ipInt) {
    return `${ipInt>>>0x18}.${(ipInt>>0x10) & 0xFF}.${(ipInt>>0x08) & 0xFF}.${ipInt & 0xFF}`
}

function getSubnet(ip) {
    const parts = ip.split("/")

    const netmask = parseInt(Array(parseInt(parts[1], 10))
        .fill("1")
        .concat(Array(32-parseInt(parts[1], 10)).fill("0"))
        .join(""), 2)

    return intToip(ipToint(parts[0]) & netmask)
}

function calculateSubnetSize(netmask) {
    let address = 0
    const octets = netmask.split(".").reverse()
    for(i = 0; i < octets.length; i++) {
        const octet = parseInt(octets[i])
        address += (octet * Math.pow(0x100,i))
    }
    return bitCount(address)
}

function bitCount (num) {
    num = num - ((num >> 1) & 0x55555555)
    num = (num & 0x33333333) + ((num >> 2) & 0x33333333)
    return ((num + (num >> 4) & 0xF0F0F0F) * 0x1010101) >> 24
}

function scanWiFi() {
    const dialog = $("#wifi-scan-dialog")
    const status = dialog.find("wifi-scan-status")
    const scanResults =  dialog.find("#wifi-scan-results")

    status.show()
    scanResults.hide()
    
    fetchJson("/wifi/scan", results => {
        
        scanResults.empty()
        for(let i = 0; i < results.length; i++) {
            const result = results[i]
            const item = $("<li></li>").text(result)
            item.click(function() {
                dialog.find("button.positive").prop("disabled", false)
            })
            scanResults.append(item)
        }

        status.hide()
        scanResults.show()
    }, reason => {
        status.text(reason.message)
    })
    
    dialog[0].showModal()
    dialog.find("button.positive").click(function() {
        const value = dialog.find("li.active").text()
        $("#wifi-ssid").val(value)
    })
    
}

$(document).ready(function() {
    fetchConfiguration()
    $("#file").on("change", parseConfigFile)
    $("#submit").click(submitConfiguration)
    $("#wifi-scan").click(scanWiFi)
});
