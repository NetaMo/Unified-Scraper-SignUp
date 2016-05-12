__author__ = 'erezlevanon'


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
