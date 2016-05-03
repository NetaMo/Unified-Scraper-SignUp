# # chatListContainer = self.browserWaitForElement(".infinite-list.chatlist")
# # chatListContainer = self.browserWaitForElement(".infinite-list-viewport")
# #
# #
# # self.browser.execute_script(Scripts.initJQuery())
# # self.browser.implicitly_wait(2)
# # self.browser.execute_script(Scripts.chatScroller(chatListContainer.size.get('height')))
# #
# # ActionChains(self.browser).move_to_element(chatListContainer).click(chatListContainer).perform()
# #
# #
# #         # moreToLoad = True
# #         # source = self.browser.page_source
# #         # while moreToLoad:
# #         #     actions.send_keys(Keys.HOME).perform()
# #         #     if source == self.browser.page_source:
# #         #         break
# #         #     source = self.browser.page_source
#
# # $( document.getElementById("some_id") ).jQueryCall();
#
# # self.browser.execute_script("return var B = []; var A = document.getElementsByClassName('message-in');  for (var i = 0; i < A.length; i++){ var b = []; var a = A[i].getElementsByClassName('emojitext');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };;")
#
#
# # Time, name and msg
# # var B = []; var A = document.getElementsByClassName('message-in');  for (var i = 0; i < A.length; i++){ var b = []; var a = A[i].getElementsByClassName('message-text');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };B
# # var B = []; var A = document.getElementsByClassName('message-in');  for (var i = 0; i < A.length;
# # i++){ var b = []; var a = A[i].getElementsByClassName('message-text');  for (var j = 0; j <
# # a.length; j++){  b.push( a[j].textContent); }  B.push(b); };B
#
#         # incomingMessages = self.browser.execute_script("var B = []; var A = "
#         #                                                "document.getElementsByClassName("
#         #                                                "'message-in');  for (var i = 0; i < "
#         #                                                "A.length; i++){ var b = []; var a = A["
#         #                                                "i].getElementsByClassName('message-text');  "
#         #                                                "for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };return B")
#
#
# var B = [];
# var A = document.getElementsByClassName('message-in');
# for (var i = 0; i < A.length; i++){
#     var b = [];
#     var a = A[i].getElementsByClassName('message-text');
#     for (var j = 0; j < a.length; j++){
#         b.push( a[j].textContent);
#     }
#     B.push(b);
# };
# return B
#
# # get time and msg, no date
# var B = [];
# var A = document.getElementsByClassName('message-in');
# for (var i = 0; i < A.length; i++){
#     var b = [A[i].getElementsByClassName('message-pre-text')[0].innerText,
#              A[i].getElementsByClassName('emojitext')[0].innerText];
#     B.push(b);
# };
# return B
# #
# # time:
# # A[0].getElementsByClassName('message-datetime')[0].innerText
# # text:
# # A[0].getElementsByClassName('emojitext')[0].innerText
#
# A[0].getElementsByClassName('message-pre-text')[0].innerText
#
# # var B = [];
# # var A = document.getElementsByClassName('message-in');
# # for (var i = 0; i < A.length; i++){
# #   var b = []; var a = A[i].getElementsByClassName('message-text');
# #   for (var j = 0; j < a.length; j++){
# #       b.push( a[j].textContent); }
# #       B.push(b);
# # };
# # B;

# This works, gets name + datetime + text
# var B = []; var A = document.getElementsByClassName('message');  for (var i = 0; i < A.length; i++){ var b = []; var a = A[i].getElementsByClassName('message-text');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };B


    # def get_person_message(self):
    #     """
    #     Get all messages from current open chat, parse to fields name, datetime and text.
    #     :return: list of messages [{"name":name, "text": text, "time":time}, {"name":name,
    #     "text": text, "time":time}, ...]
    #     """
    #     messages = []
    #     rawMessages = self.browser.execute_script("var B = []; var A = "
    #                                                "document.getElementsByClassName('message');  for (var i = 0; i < A.length; i++){ var b = []; var a = A[i].getElementsByClassName('message-text');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };return B")
    #
    #     # Extract data from raw message
    #     for msg in rawMessages:
    #
    #         name = "x"
    #         text = msg[0][0][msg[0][0].find(':')]
    #         time = msg[0][0][1:]
    #
    #         msgData = {"name":name, "text": text, "time":time}
    #         messages.append(msgData)
    #
    #     return messages