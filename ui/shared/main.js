function restJson(url, method, body, showSpinner, onResult, onError) {

    let params = {
        method: method,
        credentials: "same-origin",
        cache: "no-cache",
        headers: {}
    }
    if(body) {
        params.body = JSON.stringify(body)
        params.headers["content-type"] = "application/json"
    }

    if(showSpinner) {
        $("#loading-dialog").show()
    }

    fetch(url, params).then(response => {        
        if(response.headers.get("content-type") == "application/json") {
            response.json().then(data => {
                if(!response.ok) {
                    let input = $(`#${response.parameter}`)
                    input.addClass("error")
                    if(onError) {
                        onError(data)
                    }
                } else {
                    if(onResult) {
                        onResult(data)
                    }
                }
            })
        } else {
            if(response.ok && onResult) {
                onResult()
            }
            else if(!response.ok && onError) {
                onError(response.body)
            }
        }
        if(response.status == 401) {
            logout()          
        }
    }).then(() => {
        $("#loading-dialog").hide()
    })
}

function fetchJson(url, onResult, onError) {
    restJson(url, "GET", null, false, onResult, onError)
}

function postJson(url, data, onResult, onError) {
    restJson(url, "POST", data, true, onResult, onError)
}

function putJson(url, data, onResult, onError) {
    restJson(url, "PUT", data, true, onResult, onError)
}

function deleteJson(url, data, onResult, onError) {
    restJson(url, "DELETE", data, true, onResult, onError)
}

function genericPopulateFields(data) {
    for(const key in data) {
        let value = data[key]
        if(typeof value === "object") {
            for(const index in value) {
                $(`input#${key}-${index}`).val(value[index])
            }
        } else {
            $(`input#${key}`).val(data[key])
        }
    }
}

function getFieldData(submit) {
    configuration = {}
    submit.parents("dl.prop-grid").find("input:not(.ignore)").each(function() {
        const input = $(this)        
        configuration[input.attr("id")] = input.val()
    })

    return configuration
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
    if(window.location.pathname == "/login") {
        return
    }
    if(!getCookie("username") || !getCookie("sessionid")) {
        logout()
    }
}
