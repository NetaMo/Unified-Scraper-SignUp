# chatListContainer = self.browserWaitForElement(".infinite-list.chatlist")
# chatListContainer = self.browserWaitForElement(".infinite-list-viewport")
#
#
# self.browser.execute_script(Scripts.initJQuery())
# self.browser.implicitly_wait(2)
# self.browser.execute_script(Scripts.chatScroller(chatListContainer.size.get('height')))
#
# ActionChains(self.browser).move_to_element(chatListContainer).click(chatListContainer).perform()
#
#
#         # moreToLoad = True
#         # source = self.browser.page_source
#         # while moreToLoad:
#         #     actions.send_keys(Keys.HOME).perform()
#         #     if source == self.browser.page_source:
#         #         break
#         #     source = self.browser.page_source

# $( document.getElementById("some_id") ).jQueryCall();

# self.browser.execute_script("return var B = []; var A = document.getElementsByClassName('message-in');  for (var i = 0; i < A.length; i++){ var b = []; var a = A[i].getElementsByClassName('emojitext');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };;")


# Time, name and msg
# var B = []; var A = document.getElementsByClassName('message-in');  for (var i = 0; i < A.length; i++){ var b = []; var a = A[i].getElementsByClassName('message-text');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };B

        # incomingMessages = self.browser.execute_script("var B = []; var A = "
        #                                                "document.getElementsByClassName("
        #                                                "'message-in');  for (var i = 0; i < "
        #                                                "A.length; i++){ var b = []; var a = A["
        #                                                "i].getElementsByClassName('message-text');  "
        #                                                "for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };return B")
