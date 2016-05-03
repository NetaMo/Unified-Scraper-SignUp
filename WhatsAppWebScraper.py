import time

from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import ScrapingScripts as scraping_scripts
from Webdriver import Webdriver

# ===================================================================
# Global variables
# ===================================================================
# Server data
SERVER_POST_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# how much profile images to save
NUMBER_OF_CONTACT_PICTURES = 6


# ===================================================================
# Scraper class
# ===================================================================
class WhatsAppWebScraper:
    """
    Main class for scraping whatsapp. Receives open browser, goes to WhatsApp Web page, scrapes data
    and sends one contact at a time to the server.
    """

    def __init__(self, webdriver):
        self.browser = Webdriver.getBrowser(webdriver)  # Get browser
        self.browser.set_page_load_timeout(150)  # Set timeout to 150 seconds
        self.browser.get("https://web.whatsapp.com/")  # Navigate browser to WhatsApp page
        self.browser.execute_script(scraping_scripts.initJQuery())  # active the jquery lib

        # Wait in current page for user to log in using barcode scan.
        self.wait_for_element('.infinite-list-viewport', 300)

        # Move browser out of screen scope
        # self.browser.set_window_size(0, 0)
        # self.browser.set_window_position(-800, 600)

    # ===================================================================
    #   Main scraper function
    # ===================================================================

    def scrape(self, DB):
        print("Scraper: scrape: starting...")

        actions = ActionChains(self.browser)  # init actions option (click, send keyboard keys, etc)

        # Get to first contact chat
        searchBox = self.wait_for_element('.input.input-search')
        actions.click(searchBox).send_keys(Keys.TAB).perform()

        # Scrape each chat
        # TODO currently scrape limited amount of users for debugging
        for i in range(1, 4):

            loadStartTime = time.time()
            chat = self.__load_chat()  # load all conversations for current open chat
            print("Loaded chat in " + str(time.time() - loadStartTime) + "seconds")

            # Get contact name and type (person/group).
            contactName, contactType = self.__get_contact_details(actions)

            # Get messages from current chat
            print("Scraper: scrape: Get messages for: " + str(contactName))
            startTime = time.time()
            messages = self.__get_messages(chat, contactType, contactName)
            totalMsgTime = time.time() - startTime
            if contactType == 'group':
                print("Scraper: scrape: Got " + str(len(messages)) + " messages in " + str(totalMsgTime))
            else:
                print("Scraper: scrape: Got " + str(len(messages)) + " contact counts in " + str(totalMsgTime))

            # Initialize data item to store chat
            if contactType == 'group':
                contactData = {"contactName": contactName, "contactMessageTotal": messages[0],
                               "contactMessageCounter": messages[1]}
                print(contactData)
                DB.append_to_groups_df(contactData)

            elif contactType == 'person':
                contactData = {"contact": {"name": contactName, "type": contactType},
                               "messages": [messages]}
                DB.append_to_contacts_df(contactData)  # add data to the data frame

            # get the avatar of the contact
            # if i < NUMBER_OF_CONTACT_PICTURES:
            #     self.__get_contact_avatar()

            # go to next chat
            self.__go_to_next_contact()

        print("Scraper: scrape: finished.")

    # ===================================================================
    #   Scraper helper functions
    # ===================================================================

    def __load_chat(self):
        """
        Load to page all message for current open chat.
        """
        print("Load chat")

        actions = ActionChains(self.browser)  # init actions
        chat = self.wait_for_element('.message-list')  # wait for chat to load
        actions.click(chat).perform()

        # # JS script intended to load chat messages async
        # load_script = """
        #     continueFlag = true;
        #     // create an observer instance to monitor
        #     // any changes to the messages list
        #     var observer = new MutationObserver(
        #         // mutation callback (message loader)
        #         function(){
        #             // gets load button
        #             var btnList = document.getElementsByClassName('btn-more');
        #             // if there are no messages left, disconnect and break
        #             // otherwise, load next batch of messages
        #             if( btnList.length < 1 ) {
        #                 continueFlag = false;
        #                 observer.disconnect();
        #             }
        #             else btnList[0].click();
        #         }
        #     );
        #     // initialize observer and preempt mutation event
        #     var btnList = document.getElementsByClassName('btn-more');
        #     if( btnList.length > 0 ){
        #         // pass in the target node, as well as the observer options
        #         observer.observe(document.getElementsByClassName('message-list')[0], { childList: true });
        #         btnList[0].click();
        #     }
        #     """
        # # execute inject and execute script on browser
        # self.browser.execute_script(load_script)
        # # sample break flag every 1 second (might vary)
        # while self.browser.execute_script("return continueFlag"):
        #     time.sleep(1)

        # ----------a new faster way to load chats---------------------
        # load the chat using javascript code.
        while len(self.browser.execute_script("return $('.btn-more').click();")) is not 0:
            continue

    def __get_contact_details(self, actions):
        """
        Get contact name and type (contact/group). This is done by clicking on Chat Menu button and
        opening a submenu which contains the word Contact or Group and extracting that word.
        """
        # Get contact name
        contactName = self.browser.execute_script("return document.getElementById("
                                                  "'main').getElementsByTagName('h2');")[0].text

        # If this is a contact chat then this field will not appear
        if len(self.browser.execute_script("return document.getElementsByClassName('msg-group');")) \
                == 0:
            contactType = "person"
        else:
            contactType = "group"

        return contactName, contactType

    def __get_messages(self, chat, contactType, contactName):
        """
        Given a chat with a contact, return all messages formatted to be sent to server.
        """

        # Group chat case
        if contactType == 'group':
            return self.__get_group_messages()
        # Person chat case
        return self.__get_person_messages()

    def __get_person_messages(self):
        """
        Get all messages from current open chat, parse to fields name, datetime and text.
        :return: list of messages [{"name":name, "text": text, "time":time}, {"name":name,
        "text": text, "time":time}, ...]
        """
        messages = []
        rawMessages = self.browser.execute_script(scraping_scripts.getTextMessages())

        # Extract data from raw message
        for msg in rawMessages:
            # Unsupported messages type
            if len(msg) == 0:
                continue

            datetimeEnd = msg[0].find("]")
            dateandtime = msg[0][3:datetimeEnd]

            name = msg[0][datetimeEnd + 2:]
            nameEnd = name.find(":")
            name = name[:nameEnd]

            text = msg[0][datetimeEnd + nameEnd + 7:]

            msgData = {"name": name, "text": text, "time": dateandtime}
            print(msgData)
            messages.append(msgData)

        return messages

    def __get_group_messages(self):
        """
        Returns summary of group chat: each group member name and how many msgs they sent.
        @:return list of len 2: [int totalMessages , dict {"Asaf":360, "Neta":180,...}]
        """

        groupData = {}  # data to be returned
        lastName = None  # last known name to send a msg, used for msgs without author name

        # Get all incoming messages, only the author name and text.
        # this script looks for class "message-in" then "emojitext" then takes .innerText
        incomingMessages = self.browser.execute_script(scraping_scripts.getIncomingMessages())
        totalMessages = len(incomingMessages)

        for msg in incomingMessages:
            # If has author name, check if exists then update, if doesn't exists create it.
            if len(msg) == 2:
                lastName = msg[0]
                if lastName in groupData:
                    groupData[lastName] += 1
                    continue
                else:
                    groupData[lastName] = 1
                    continue

            # If no author name in msg, take last name
            # TODO handle image, video, etc.
            elif len(msg) == 1 and msg[0] in groupData:
                lastName = msg[0]

            groupData[lastName] += 1

        # print("getGroupMessages got " + str(len(incomingMessages)) + " messages, here they are:")
        # print(str(groupData))
        return [totalMessages, groupData]

    def __get_contact_avatar(self):
        """
        Sends to db the avatar of current loaded chat.
        """
        print("Scraper: scrape: __get_contact_avatar started...")

        # Getting the small image's url and switching to the large image
        avatar_url = self.browser.execute_script("return $('#main header div.chat-avatar div "
                                                 "img');").get_attribute("src")
        avatar_url = avatar_url[:34] + "l" + avatar_url[35:]

        # Opening a new tab
        actions = ActionChains(self.browser)
        actions.send_keys(Keys.CONTROL).send_keys('t').perform()

        # Switching to the new tab and navigating to image's url
        defWin = self.browser.window_handles[0]
        newWin = self.browser.window_handles[1]
        self.browser.switch_to_window(newWin)
        self.browser.get(avatar_url)

        # Saving a screen shot
        self.wait_for_element('body img')

        # Getting image size for cropping
        img = self.browser.execute_script("return $('body img');")
        width = img.get_attribute("width")
        height = img.get_attribute("height")
        self.browser.save_screenshot("full_screen_shot_temp.png")

        # Cropping
        screenshot = Image.open("full_screen_shot_temp.png")
        cropped = screenshot.crop((0, 0, int(width), int(height)))
        cropped.save("contact_avatar.jpg")

        # Closing the tab
        actions.send_keys(Keys.CONTROL).send_keys('w').perform()
        self.browser.switch_to_window(defWin)

        print("Scraper: scrape: __get_contact_avatar ended.")

    def __go_to_next_contact(self, isFirst=False):
        """
        Goes to next contact chat in contact list. This is done by locating the "search" box and
        pressing tab and then arrow down.
        """
        actions = ActionChains(self.browser)
        actions.click(self.wait_for_element('.input.input-search')).perform()
        actions.send_keys(Keys.TAB).send_keys(Keys.ARROW_DOWN).perform()

    # ===================================================================
    #   Webdriver helper functions
    # ===================================================================

    def wait_for_element(self, jquerySelector, timeout=10):
        """
        General helper function. Searches and waits for css element to appear on page and returns it,
        if it doesnt appear after timeout seconds prints relevant exception and returns None.
        """
        startTime = time.time()
        elements = self.browser.execute_script("return $(arguments[0]);", jquerySelector)

        while (len(elements) == 0):
            elements = self.browser.execute_script("return $(arguments[0]);", jquerySelector)
            if time.time() - startTime > timeout:
                return None

        return elements[0]
