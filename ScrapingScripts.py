def initJQuery():
    # add jquery
    with open("jquery-2.2.3.min.js", 'r') as jquery_js:
        jquery = jquery_js.read()  # read the jquery from a file
        return jquery


def getTextMessages():
    return "var B = []; var A = document.getElementsByClassName('message');  for (var i = 0; i < " \
           "A.length; i++){ var b = []; var a = A[i].getElementsByClassName('message-text');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };return B"


def getIncomingMessages():
    return "var B = []; var A = document.getElementsByClassName('message-in');  for (var i = 0; i < A.length; i++){ var b = []; var a = A[i].getElementsByClassName('emojitext');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };;return B"

    # def initJQuery():
    #     return "var jq = document.createElement('script');" \
    #            "jq.src =\"https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js\";\
    #             document.getElementsByTagName('head')[0].appendChild(jq);"

    # def chatScroller(scrollHeight):
    #     return "jQuery.noConflict();\
    #             $ = jQuery;\
    #             $(\"#pane-side\").animate({scrollTop:  " + str(scrollHeight) + "});"

    # # Doesnt work.
    # def getUserNameScript():
    #     return "var nameField = document.getElementById('nameField').value;\
    #             var result = document.getElementById('result');\
    #             if (nameField.length < 3) {\
    #                 result.textContent = 'Username must contain at least 3 characters';\
    #                 //alert('Username must contain at least 3 characters');\
    #             } else {\
    #                 result.textContent = 'Your username is: ' + nameField;\
    #                 //alert(nameField);\
    #             }\
    #             jQuery.ajax({\
    #                 url: 'localhost:8888/userName',\
    #                 contentType: \"application/json; charset=utf-8\",\
    #                 data: JSON.stringify({\"userName\":result.textContent}),\
    #                 type: #'POST',\
    #                 success: function(response) {\
    #                     console.log(response);\
    #                 },\
    #                 error: function(error) {\
    #                     console.log(error);\
    #                 }\
    #             });"
