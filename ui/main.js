async function fetchJson(path) {
    return await (await fetch(path)).json()
}

function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function eraseCookie(name) {   
    document.cookie = name+'=; Max-Age=-99999999;';  
}

function logout() {
    eraseCookie("username")
    eraseCookie("sessionid")
    location.href = "/login"
}

$(document).ready(function() {
    $("div.template").each(function() {
        let url = $(this).attr("data-content")
        let script = $(this).attr("data-script")
        if(url) {
            $(this).load(url)

            if(script) {
                $.getScript(script)
            }

        } else {
            console.log("Warning: template with no content url.")
        }
    })

    checkLogin()
});

function checkLogin() {
    if(!getCookie("username") || !getCookie("sessionid")) {
        logout()
    }
}
