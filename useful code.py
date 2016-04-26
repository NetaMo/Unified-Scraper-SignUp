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