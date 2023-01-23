function fixAutofill(ids) {
    setTimeout(function() {

        const selector = ids.map(function(value) {
            return `#${value}`
        }).join(",")

        $(selector).val("")
    }, 500)
}
