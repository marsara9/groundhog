

function genericPopulateFields(data, prefix = null) {
    for(const key in data) {
        let value = data[key]

        const next = (prefix ? `${prefix}-${key}` : key)
        const id = `input#${next}`

        if(value instanceof Object) {
            genericPopulateFields(value, next)
        } else {
            $(id).val(value)
        }
    }
}

function getFieldData(submit) {
    let configuration = {}
    submit.parents("dl.prop-grid").find("input:not(.ignore)").each(function() {
        const input = $(this)
        const value = input.val()

        if(!value) {
            return
        }

        let object = value

        const keys = input.attr("id").split("-")
        for(let i = keys.length-1; i >= 0; i--) {
            const key = keys[i]

            const temp = (isNaN(parseInt(key, 10)) ? {} : [])
            temp[key] = object
            object = temp
        }

        configuration = _.merge(configuration, object)
    })

    return configuration
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

function configureListSelect() {
    $("ul.select > li").click(function () {
        $(this).siblings("li.active").removeClass("active")
        $(this).addClass("active")
    })
}

$(document).ready(function() {
    loadTemplates()
    
    setupTabs()
    configureListSelect()

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
