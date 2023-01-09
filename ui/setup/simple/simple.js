function fetchConfiguration() {
    fetchJson("/simple/configuration", result => {
        genericPopulateFields(result)

        const localIpAddress = result["lan-ip"]
        const ip = localIpAddress.split("/")[0]
        const netmask = localIpAddress.split("/")[1]

        $("#lan-ip").val(localIpAddress.split("/")[0])
        $("#subnet").text(`${getSubnet(localIpAddress)}/${netmask}`)
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
