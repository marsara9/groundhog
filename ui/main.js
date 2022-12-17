async function fetchJson(path) {
    return await (await fetch(path)).json()
}

$(function() {
    $("div.template").each(function() {
        let url = $(this).attr("data-content")
        if(url) {
            $(this).load(url)
        } else {
            console.log("Warning: template with no content url.")
        }
    })

    checkLogin()
});

function checkLogin() {

}