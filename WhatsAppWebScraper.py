import time

import selenium.webdriver.support.expected_conditions as ec
from PIL import Image
from selenium.common.exceptions import TimeoutException, \
    StaleElementReferenceException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

import ScrapingScripts as SS
from Webdriver import Webdriver

# ===================================================================
# Global variables
# ===================================================================
# Server data
SERVER_URL_CHAT = "http://localhost:8888/chat"
SERVER_URL_FINISHED = "http://localhost:8888/chatFinished"
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

        # Wait in current page for user to log in using barcode scan.
        self.wait_for_element(".infinite-list-viewport", 300)

        # Move browser out of screen scope
        # self.browser.set_window_size(0, 0)
        # self.browser.set_window_position(-800, 600)

        self.browser.execute_script(SS.initJQuery())  # active the jquery lib

    # ===================================================================
    #   Main scraper function
    # ===================================================================

    def scrape(self, DB):
        print("start scraping")

        actions = ActionChains(self.browser)  # init actions option (click, send keyboard keys, etc)

        # Get to first contact chat
        searchBox = self.wait_for_element(".input.input-search")
        actions.click(searchBox).send_keys(Keys.TAB).perform()

        # Scrape each chat
        # TODO currently scrape limited amount of users for debugging
        for i in range(1, 5):

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
            print("Scraper: scrape: Got " + str(len(messages)) + " messages in " + str(totalMsgTime))

            # Initialize data item to store chat
            if contactType == 'group':
                contactData = {"contactName": contactName, "contactMessageTotal": messages[ 0 ],
                               "contactMessageCounter": messages[ 1 ]}
                print(contactData)
                DB.append_to_groups_df(contactData)

            elif contactType == 'person':
                contactData = {"contact": {"name": contactName, "type": contactType},
                               "messages": [ messages ]}
                DB.append_to_contacts_df(contactData)  # add data to the data frame

            # get the avatar of the contact
            # if i < NUMBER_OF_CONTACT_PICTURES:
            #     self.get_contact_avatar()

            # go to next chat
            self.__go_to_next_contact()

        print("done scraping")

    # ===================================================================
    #   Scraper helper functions
    # ===================================================================

    def __load_chat(self):
        """
        Load to page all message for current open chat.
        """
        print("Load chat")

        actions = ActionChains(self.browser)  # init actions
        chat = self.wait_for_element(".message-list")  # wait for chat to load
        actions.click(chat).perform()

        # load the chat using javascript code.
        while len(self.browser.execute_script("return $('.btn-more').click();")) is not 0:
            continue

            # Try #1.
            # self.browser.execute_script("btnMore = $('.btn-more');")
            # btnMoreCounter = 0
            # while len(self.browser.execute_script("return btnMore.click();")) is not 0:
            #     # time.sleep(0.0001)
            #     btnMoreCounter += 1
            #     if btnMoreCounter % 500 == 0:
            #         print("------" + str(btnMoreCounter) + " iterations of btnMore: ")
            #         self.browser.execute_script("btnMore = $('.btn-more');a")
            #     continue

            # counter = 0
            # # load previous messages until no "btn-more" exists
            # #     currently loads 10 previous message.
            # # while counter < 20:
            # while True:
            #     counter += 1
            #     btnMore = self.waitForElement(".btn-more", 2)
            #     if btnMore is not None:
            #         try:
            #             actions.click(btnMore).perform()
            #         except StaleElementReferenceException as e:
            #             break
            #     else:
            #         break

    def __get_contact_details(self, actions):
        """
        Get contact name and type (contact/group). This is done by clicking on Chat Menu button and
        opening a submenu which contains the word Contact or Group and extracting that word.
        """
        # Get contact name
        contactName = self.browser.execute_script("return document.getElementById("
                                                  "'main').getElementsByTagName('h2');")[ 0 ].text

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
        messages = [ ]
        rawMessages = self.browser.execute_script(SS.getTextMessages())

        # Extract data from raw message
        for msg in rawMessages:
            # Unsupported messages type
            if len(msg) == 0:
                continue

            datetimeEnd = msg[ 0 ].find("]")
            dateandtime = msg[ 0 ][ 3:datetimeEnd ]

            name = msg[ 0 ][ datetimeEnd + 2: ]
            nameEnd = name.find(":")
            name = name[ :nameEnd ]

            text = msg[ 0 ][ datetimeEnd + nameEnd + 7: ]

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
        incomingMessages = self.browser.execute_script(SS.getIncomingMessages())
        totalMessages = len(incomingMessages)

        for msg in incomingMessages:
            # If has author name, check if exists then update, if doesn't exists create it.
            if len(msg) == 2:
                lastName = msg[ 0 ]
                if lastName in groupData:
                    groupData[ lastName ] += 1
                    continue
                else:
                    groupData[ lastName ] = 1
                    continue

            # If no author name in msg, take last name
            # TODO handle image, video, etc.
            elif len(msg) == 1 and msg[ 0 ] in groupData:
                lastName = msg[ 0 ]

            groupData[ lastName ] += 1

        # print("getGroupMessages got " + str(len(incomingMessages)) + " messages, here they are:")
        # print(str(groupData))
        return [ totalMessages, groupData ]

    def __get_contact_avatar(self):
        """
        Sends to db the avatar of current loaded chat.
        """
        print("In getContactAvatar")
        # Getting the small image's url and switching to the large image
        avatar_url = self.browser.execute_script("return $('#main header div.chat-avatar div "
                                                 "img');").get_attribute("src")
        avatar_url = avatar_url[ :34 ] + "l" + avatar_url[ 35: ]

        # Opening a new tab
        actions = ActionChains(self.browser)
        actions.send_keys(Keys.CONTROL).send_keys('t').perform()

        # Switching to the new tab and navigating to image's url
        defWin = self.browser.window_handles[ 0 ]
        newWin = self.browser.window_handles[ 1 ]
        self.browser.switch_to_window(newWin)
        self.browser.get(avatar_url)

        # Saving a screen shot
        self.wait_for_element("body img")

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

    def __go_to_next_contact(self, isFirst=False):
        """
        Goes to next contact chat in contact list. This is done by locating the "search" box and
        pressing tab and then arrow down.
        """
        actions = ActionChains(self.browser)
        actions.click(self.wait_for_element(".input.input-search")).perform()
        actions.send_keys(Keys.TAB).send_keys(Keys.ARROW_DOWN).perform()

    # ===================================================================
    #   Webdriver helper functions
    # ===================================================================

    def wait_for_element(self, cssSelector, timeout=10, cssContainer=None, singleElement=True):
        """
        General helper function. Searches and waits for css element to appear on page and returns it,
        if it doesnt appear after timeout seconds prints relevant exception and returns None.
        """
        # print("Wait for element: " + cssSelector)
        if cssContainer is None:
            cssContainer = self.browser

        try:
            elements = WebDriverWait(cssContainer, timeout). \
                until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, cssSelector)))
            # print("Done waiting for element: " + cssSelector)
            if singleElement:
                return elements[ 0 ]
            return elements
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            print("Exception for element " + str(cssSelector) + " on page: " + str(
                    self.browser.current_url))
            return None

            # def get_element(self, cssSelector, cssContainer = None):
            #     """
            #     Helper function. Searches for element by css selector, if it doesn't exists catchs
            #     NoSuchElementException and returns None.
            #     """
            #     if cssContainer is None:
            #         cssContainer = self.browser
            #     try:
            #         return cssContainer.find_element_by_css_selector(cssSelector)
            #     except (NoSuchElementException, StaleElementReferenceException):
            #         return None
