function fetchDHCPConfig() {
    fetchJson("/dhcp/configuration", result => {
        genericPopulateFields(result)

        $("#netmask").text(`/${calculateSubnetSize(result.netmask)}`)
    })
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
    fetchDHCPConfig()
});