def initJQuery():
    return "var jq = document.createElement('script');" \
           "jq.src =\"https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js\";\
            document.getElementsByTagName('head')[0].appendChild(jq);"

def chatScroller(scrollHeight):
    return "jQuery.noConflict();\
            $ = jQuery;\
            $(\"#pane-side\").animate({scrollTop:  " + str(scrollHeight) + "});"

# TODO : this is not working currently
def getUserNameScript():
    return "    var nameField = document.getElementById('nameField').value;\
            var result = document.getElementById('result');\
            if (nameField.length < 3) {\
                result.textContent = 'Username must contain at least 3 characters';\
                //alert('Username must contain at least 3 characters');\
            } else {\
                result.textContent = 'Your username is: ' + nameField;\
                //alert(nameField);\
            }\
            jQuery.ajax({\
                url: 'localhost:8888/userName',\
                contentType: \"application/json; charset=utf-8\",\
                data: JSON.stringify({\"userName\":result.textContent}),\
                type: 'POST',\
                success: function(response) {\
                    console.log(response);\
                },\
                error: function(error) {\
                    console.log(error);\
                }\
            });"