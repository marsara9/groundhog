function fetchDHCPConfig() {
    fetchJson("/dhcp/configuration", result => {
        
    })
}

$(document).ready(function() {
    fetchDHCPConfig()
});