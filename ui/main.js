async function fetchJson(path) {
    return await (await fetch(path)).json()
}

const observer = new MutationObserver(function () {
    observer.disconnect()
})

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

function loadTemplates() {
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
}

function setupTabs() {
    $(".tabbar").each(function() {
        const tabs = $(this).children("button.tab")
        tabs.each(function() {
            $($(this).attr("data-content")).hide()
            $(this).click(function() {
                tabs.each(function() {
                    $(this).removeClass("selected")
                    $($(this).attr("data-content")).hide()
                })

                $(this).addClass("selected")
                $($(this).attr("data-content")).show()
            })
        })
        tabs.first().click()
    })
}

function fixAutoFill() {
    // $("input").each(function() {
    //     $(this).attr("readonly", "readonly")
    // })
    // setTimeout(function() {
    //     $("input").each(function() {
    //         $(this).removeAttr("readonly")
    //         $(this).val("")
    //     })
    // }, 500)
}

$(document).ready(function() {
    loadTemplates()
    setupTabs()
    checkLogin()
    fixAutoFill()
});

function checkLogin() {
    if(!getCookie("username") || !getCookie("sessionid")) {
        logout()
    }
}
