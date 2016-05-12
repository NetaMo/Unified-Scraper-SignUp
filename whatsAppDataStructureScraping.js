/**
 * Created by elevanon on 5/10/2016.
 */

// get contacts by activity level

var allContacts = [];
var curContactName;
var curChat;
var savedChats = 0;
var interval;
var numOfMsgs;
var intensity;

var lineSeperator = "------------------------------------------";

console.log(lineSeperator);
var i, j = 0;
for (i = 0; i < Store.Chat.models.length; i++) {

    // get a chat
    curChat = Store.Chat.models[i];

    // only run if it's a user.
    if (!curChat.isUser)
    {
        continue;
    }

    curContactName = curChat.formattedTitle;
    console.log("Calculating " + curContactName);
    // get type - and only continue if a user or a group (no broadcast list etc.)

    // get num of msgs
    numOfMsgs = curChat.msgs.models.length;

    //get difference between first and last message

    interval = (curChat.msgs.models[numOfMsgs-1].t - curChat.msgs.models[0].t);

    intensity = numOfMsgs / interval;

    allContacts.push({name:curContactName, rank:intensity});
    savedChats++;
}
console.log("calculated " + savedChats + " chats");
console.log(lineSeperator);
allContacts;


// get All first messages (iterating on Chat)
//
//var allContacts = [];
//var curDict;
//var curContactName;
//var curMsgName;
//var curMsgTime;
//var curType;
//var curMsgText;
//var curMsgObject;
//var curMsg;
//var curChat;
//var curNumOfMsgs;
//var savedChats = 0;
//
//var lineSeperator = "------------------------------------------";
//
//console.log(lineSeperator);
//var i, j = 0;
//for (i = 0; i < Store.Chat.models.length; i++) {
//
//    //get a chat and it's name
//    curChat = Store.Chat.models[i]
//    curContactName = curChat.formattedTitle;
//    console.log("Scraping " + curContactName);
//    // get type - and only continue if a user or a group (no broadcast list etc.)
//    if (curChat.isUser)
//    {
//        curType = "person";
//    }
//    else if (curChat.isGroup)
//    {
//        curType = "group";
//        continue;
//    }
//    else
//    {
//        continue;
//    }
//
//    console.log("\tit's a " + curType);
//
//    //initialize this chat's dict
//    curDict = {contact:{type:curType, name:curContactName, messages:[]}};
//
//    //
//    for (j = 0; j < curChat.msgs.models.length ; j++)
//    {
//        // get a message
//        curMsgObj = curChat.msgs.models[j];
//        if (curMsgObj.isMMS  || curMsgObj.isMedia || curMsgObj.isNotification )
//        {
//            continue;
//        }
//        // construct message object
//        curMsgName = curMsgObj.senderObj.formattedName;
//        curMsgTime = curMsgObj.t;
//        curMsgText = curMsgObj.body;
//        curMsg = {name:curMsgName, time:curMsgTime, text:curMsgText}
//        curDict.contact.messages.push(curMsg);
//    }
//
//    // get number of messages
//    curNumOfMsgs = curDict.contact.messages.length;
//
//    console.log("\t got " + curNumOfMsgs + " messages");
//
//    if (curNumOfMsgs != 0)
//    {
//        savedChats++;
//        allContacts.push(curDict);
//    }
//    console.log(lineSeperator);
//}
//console.log("saved " + savedChats + " chats");
//console.log(lineSeperator);
//allContacts;


//// get ALL info (iterating via messages)
//var allContacts = [];
//var curDict;
//var lastContact = "place holder";
//var isGroup;
//var curContactName;
//var curMsgName;
//var curMsgTime;
//var curType;
//var curText;
//var curMsg;
//
//console.log("------------------------------------");
//var i, j = 0;
//var started = false;
//for (i = j = 0; i < Store.Msg.models.length; i++) {
//    curContactName = Store.Msg.models[i]["chat"]["formattedTitle"];
//    if(curContactName != lastContact)
//    {
//        if (started)
//        {
//            allContacts.push(curDict);
//        }
//        console.log("scraping " + curContactName);
//        curType = "person";
//        if (Store.Msg.models[i]["isGroupMsg"])
//        {
//            curType = "group";
//        }
//        curDict = {contact:{type:curType, name:curContactName, messages:[]}}
//        console.log("\tit's a " + curType);
//        if (started)
//        {
//            console.log("\t got " + (i -j) + " messages");
//            j = i;
//        }
//        console.log("------------------------------------");
//        lastContact = curContactName;
//        started = true;
//    }
//    curMsgName  = Store.Msg["models"][i]["senderObj"]["formattedTitle"];
//    curMsgTime  = Store.Msg["models"][i]["t"];
//    curText     = Store.Msg["models"][i]["body"];
//    curMsg     = {time:curMsgTime, name:curMsgName, text:curText};
//    curDict.contact.messages.push(curMsg);
//}
//allContacts;


// try get contact + message
//result = [];
//var lastContact = "place holder";
//var i, j;
//for (i = j = 0; i < Store.Msg.models.length; i++) {
//    console.log("------------------------------------")
//    if (Store.Msg.models[i]["isGroupMsg"])
//    {
//        console.log("in group, passing " + Store.Msg.models[i]["chat"]["formattedTitle"]);
//        i += Store.Msg.models[i]["msgChunk"]["models"].length;
//        continue;
//    }
//    if (Store.Msg.models[i]["isSentByMe"])
//    {
//        continue;
//    }
//    if(Store.Msg.models[i]["chat"]["formattedTitle"] != lastContact)
//    {
//        console.log(Store.Msg.models[i]["chat"]["formattedTitle"]);
//        console.log("\t" + Store.Msg.models[i]["body"]);
//        lastContact = Store.Msg.models[i]["chat"]["formattedTitle"];
//        result[j] = {contactName:Store.Msg.models[i]["chat"]["formattedTitle"], text:Store.Msg.models[i]["body"]};
//        j++;
//    }
//}
//result

// create array of contacts
//result = [];
//for (i = j = 0; i < Store.Contact.models.length; i++) {
//    curName = Store.Contact.models[i];
//    if(curName["isUser"]){
//        if(!(curName["isMe"])){
//            result[j] = curName["formattedName"];
//            j++;
//        }
//    }
//}
//result