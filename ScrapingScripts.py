def initJQuery():
    # add jquery
    with open("jquery-2.2.3.min.js", 'r') as jquery_js:
        jquery = jquery_js.read()  # read the jquery from a file
        return jquery


def initMoment():
    # add moment
    with open("moment-with-locales.js", 'r', encoding="utf-8") as jquery_js:
        jquery = jquery_js.read()  # read the jquery from a file
        return jquery

def getTextMessages():
    return '''
        var B = [];
        var A = document.getElementsByClassName('message');
        for (var i = 0; i < A.length; i++) {
            var b = [];
            var a = A[i].getElementsByClassName('message-text');
            var c = A[i].getElementsByClassName('link-preview-container')
            var d = A[i].getElementsByClassName('quoted-msg')
            if (a.length != 0 && c.length == 0 && d.length == 0){
                for (var j = 0; j < a.length; j++) {
                    end_pos = a[0].innerText.indexOf("]");

                    var currentDate = a[0].innerText.slice(0, end_pos).replace(",", "").replace("[", "").replace("]", "");
                    //console.log("OLD:" + currentDate);
                    //if (currentDate.indexOf("2015") == -1 && currentDate.indexOf("2016") == -1) {
                    //    //console.log(currentDate)
                    //}
                    // substring(2,length) because 2 first invisible charachters.............. ^_^
                    // var formattedDate = this.moment(currentDate.substring(2,currentDate.length), moment.localeData()._longDateFormat.LT + ' ' +
                    // moment.localeData()._longDateFormat.l).format("HH:mm MM/DD/YYYY");
                    var formattedDate = this.moment(currentDate.substring(2,currentDate.length)).format("HH:mm MM/DD/YYYY");
                    //if (currentDate.indexOf("2015") == -1 && currentDate.indexOf("2016") == -1) {
                    //    //console.log(currentDate)
                    //}
                    // substring(2,length) because 2 first invisible charachters.............. ^_^
                    // var formattedDate = this.moment(currentDate.substring(2,currentDate.length), moment.localeData()._longDateFormat.LT + ' ' +
                    // moment.localeData()._longDateFormat.l).format("HH:mm MM/DD/YYYY");
                    var formattedDate = this.moment(currentDate.substring(2,currentDate.length)).format("HH:mm MM/DD/YYYY");
                    b.push(a[j].innerText);
                }
                console.log("NEW" + formattedDate);
                if (b.length != 0) {
                    //console.log(b[0]);
                    b[0] = '[' + formattedDate + '] ' + b[0].slice(end_pos+1);
                }
                B.push(b);
                // if (A[i].getElementsByClassName('message-text message-link').length != 0) {
                if (A[i].getElementsByClassName('link-preview-container').length != 0) {
                    B[i] = [];
                };
            };
        };
        return B;
        '''

def getSingleTextMessageFromSearch():
    return '''
            var active = document.getElementsByClassName('message active chat');
            name = active[0].getElementsByClassName('chat-title')[0].innerText
            msg = active[0].getElementsByClassName('chat-status')[0].innerText;
            return [name, msg];
        '''

def getSearchResults():
    return '''
        var results = [];
        var messages = document.getElementsByClassName('message chat');
        for (var i = 0; i < messages.length; i++) {
            var result_item = messages[i];
            var contact_name = result_item.getElementsByClassName('chat-title')[0].innerText;
            results.push(contact_name);
        }
        return results;
    '''

def isConversation():
    return '''
        var active = document.getElementsByClassName('message active chat');
        if (active.length !== 1) {
            return false;
        }
        return true;
    '''


def getSingleOutgoingMessage():
    return ''' var A = document.getElementsByClassName('message message-out')
               if (A.length != 0){
                    a = A[0].getElementsByClassName('message-text');
                    if(a.length != 0 ){
                        return A[0].innerText;
                    }
                }
                return [];
            '''

def getIncomingMessages():
    return """"
        var B = [];
        var A = document.getElementsByClassName('message-in');
        for (var i = 0; i < A.length; i++) {
            var b = [];
            var a = A[i].getElementsByClassName('emojitext');
            for (var j = 0; j < a.length; j++) {
                b.push(a[j].innerText);
            }
            B.push(b);
        };;
        return B
    """

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


def getAllFirstMessages():
    """
    Gets data from Store object.
    :return: format to fit db
    """
    return '''

    // get All first messages (iterating on Chat)

    var allContacts = [];
    var curDict;
    var lastContact = "place holder";
    var isGroup;
    var curContactName;
    var curMsgName;
    var curMsgTime;
    var curType;
    var curMsgText;
    var curMsg;
    var curChat;
    var curNumOfMsgs;
    var savedChats = 0;

    var lineSeperator = "------------------------------------------";

    console.log(lineSeperator);
    var i, j = 0;
    for (i = 0; i < Store.Chat.models.length; i++) {

        //get a chat and it's name
        curChat = Store.Chat.models[i]
        curContactName = curChat.formattedTitle;
        console.log("Scraping " + curContactName);
        // get type - and only continue if a user or a group (no broadcast list etc.)
        if (curChat.isUser)
        {
            curType = "person";
        }
        else if (curChat.isGroup)
        {
            curType = "group"
            continue;
        }
        else
        {
            continue;
        }

        console.log("\tit's a " + curType);

        //initialize this chat's dict
        curDict = {contact:{type:curType, name:curContactName, messages:[]}};

        //
        for (j = 0; j < curChat.msgs.models.length ; j++)
        {
            // get a message
            curMsgObj = curChat.msgs.models[j];
            if (curMsgObj.isMMS  || curMsgObj.isMedia || curMsgObj.isNotification )
            {
                continue;
            }
            // construct message object
            curMsgName = curMsgObj.senderObj.formattedName;
            curMsgTime = curMsgObj.t;
            curMsgText = curMsgObj.body;
            curMsg = {name:curMsgName, time:curMsgTime, text:curMsgText}
            curDict.contact.messages.push(curMsg);
        }

        // get number of messages
        curNumOfMsgs = curDict.contact.messages.length;

        console.log("\t got " + curNumOfMsgs + " messages");

        if (curNumOfMsgs != 0)
        {
            savedChats++;
            allContacts.push(curDict);
        }
        console.log(lineSeperator);
    }
    console.log("saved " + savedChats + " chats");
    console.log(lineSeperator);
    return allContacts;

    '''

def get_latest_k_chats(k):      # todo small_time!!
    return '''
    var chats = [];
    var k = parseInt("''' + str(k) + '''");

    for (i = 0; i < k; i++) {
        curChat = Store.Chat.models[i];
        if (!curChat.isUser) {
            ++k;
            if ((Store.Chat.models.length-1) == k) {
                return chats;
            }
            continue;
        }
        name = curChat.formattedTitle;
        msg = curChat.msgs.models[curChat.msgs.models.length -1].body;
        small_time = "21:30"

        chats.push({
            contactName: name,
            text : msg,
            time: small_time
        });
    }

    return chats;
    '''

def amphi(curName, nickname):
    command = '''
    var allContacts = [];
    var curContactName;
    var curChat;
    var curMsg;
    var savedChats = 0;
    var numOfMsgs;
    var found;

    var lineSeperator = "------------------------------------------";

    console.log(lineSeperator);
    var i, j = 0;
    for (i = 0; i < Store.Chat.models.length; i++) {

        // get a chat
        curChat = Store.Chat.models[i];

        // only run if it's a user.
        if (!curChat.isUser) {
            continue;
        }

        curContactName = curChat.formattedTitle;
        console.log("	Calculating " + curChat.formattedTitle);
        // get type - and only continue if a user or a group (no broadcast list
        // etc.)

        // get num of msgs
        numOfMsgs = curChat.msgs.models.length;
        found = false;
        curMsg = "''' + curName + '''";
        for (var j = 0; j < numOfMsgs; j++) {
            if (typeof(curChat.msgs.models[j].body) !=
                "undefined") {
                if (curChat.msgs.models[j].body.search("''' + curName + '''") != -1 ||
                    curChat.msgs.models[j].body.search("''' + nickname + '''") !=
                    -1) {
                    curMsg = curChat.msgs.models[j].body;
                }
            }
        }

        allContacts.push({
            name: curContactName, rank: numOfMsgs,
            text: curMsg
        });
        savedChats++;
    }
    console.log("	calculated " + savedChats + " chats");
    console.log(lineSeperator);
    return allContacts;
                '''

    return command