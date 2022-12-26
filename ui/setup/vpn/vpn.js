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
    // reader.readAsDataURL(file)
    reader.readAsText(file)
}

function setConfiguration(configuration) {
    const endpoint = configuration.endpoint.split(":")[0]
    const port = configuration.endpoint.split(":")[1]
    $("#endpoint").val(endpoint)
    $("#port").val(port)

    $("#privatekey").val(configuration.privatekey)
    $("#publickey").val(configuration.publickey)
    $("#presharedkey").val(configuration.presharedkey)

    $("#address").val(configuration.address)
    $("#dns").val(configuration.dns)
    $("#allowedips").val(configuration.allowedips)
}

$(document).ready(function() {
    $("#file").on("change", parseConfigFile)    
});

