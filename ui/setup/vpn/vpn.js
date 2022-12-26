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
    $("#url").val(url)
    $("#port").val(port)
    $("#endpoint").val(configuration.endpoint)

    $("#privatekey").val(configuration.privatekey)
    $("#publickey").val(configuration.publickey)
    $("#presharedkey").val(configuration.presharedkey)

    $("#address").val(configuration.address)
    $("#dns").val(configuration.dns)
    $("#allowedips").val(configuration.allowedips)
}

function getConfiguration(submit) {
    configuration = {}
    submit.parents("dl.prop-grid").find("input:not(.ignore)").each(function() {
        const input = $(this)        
        configuration[input.attr("id")] = input.val()
    })

    return configuration
}

function submitConfiguration() {
    putJson("/configuration/vpn", getConfiguration($(this)))
}

$(document).ready(function() {

    $("#url").on("input", function() {
        $("#endpoint").val($(this).val() + ":" + $("#port").val())
    })
    $("#port").on("input", function() {
        $("#endpoint").val($("#url").val() + ":" + $(this).val())
    })

    $("#file").on("change", parseConfigFile)
    $("#submit").click(submitConfiguration)
});

