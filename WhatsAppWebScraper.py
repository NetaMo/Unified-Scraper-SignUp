import time

from PIL import Image, ImageChops
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import ScrapingScripts as scrapingScripts
from Webdriver import Webdriver

# ===================================================================
# Global variables
# ===================================================================
# Server data
SERVER_POST_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# how much profile images to save
NUMBER_OF_CONTACT_PICTURES = 6
# Where to save temporary images for avatars
TEMP_AVATAR_PATH = "static/tempAvatars/contact_avatar"
TEMP_SCREENSHOT_PATH = "full_screen_shot_temp.png"

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
        self.browser.execute_script(scrapingScripts.initJQuery())  # active the jquery lib
        self.scrapedContacts = [ ]  # List of scraped contacts
        self.defaultAvatar = Image.open("defaultAvatar.jpg")
        self.user_whatsapp_name = None

        # Wait in current page for user to log in using barcode scan.
        self.wait_for_element('.infinite-list-viewport', 300)

        # Move browser out of screen scope
        # self.browser.set_window_size(0, 0)
        # self.browser.set_window_position(-999, 999)

    # ===================================================================
    #   Main scraper function
    # ===================================================================

    def scrape(self, DB):
        print("Scraper: scrape: starting...")
        scrapeStartTime, scrapeTotalMsgs = time.time(), 0

        # Get to first contact chat
        actions = ActionChains(self.browser)  # init actions option (click, send keyboard keys, etc)
        actions.click(self.wait_for_element('.input.input-search')).send_keys(Keys.TAB).perform()

        # List of contacts we already scraped, in case user get new message while scraping
        scraped_contacts = []

        # Scrape each chat
        # TODO currently scrape limited amount of users for debugging

        for i in range(1, 15):
            loadStartTime = time.time()
            self.__load_chat()  # load all conversations for current open chat
            print("Loaded chat in " + str(time.time() - loadStartTime) + "seconds")

            # Get contact name and type (person/group).
            get_contact_time = time.time()
            contactName, contactType = self.__get_contact_details()
            print("Got Contact details in " + str(time.time() - get_contact_time) + "seconds")

            # If the user received message while scraping we don't want to scrape it again
            if contactName in scraped_contacts:
                self.__go_to_next_contact()
                i -= 1  # TODO When changing to dynamic iteration should be handled differently
                continue

            # Get messages from current chat
            print("Scraper: scrape: Get messages for: " + str(contactName))
            startTime = time.time()
            messages = self.__get_messages(contactType, contactName)
            totalMsgTime = time.time() - startTime

            if contactType == 'group':
                print(
                    "Scraper: scrape: Got " + str(messages[ 0 ]) + " messages in " + str(totalMsgTime))
                scrapeTotalMsgs += messages[0]
            else:
                print("Scraper: scrape: Got " + str(len(messages)) + " messages in " + str(
                        totalMsgTime))
                scrapeTotalMsgs += len(messages)

            # Initialize data item to store chat
            if contactType == 'group':
                contactData = {"contactName": contactName, "contactMessageTotal": messages[ 0 ],
                               "contactMessageCounter": messages[ 1 ]}
                DB.append_to_groups_df(contactData)

            elif contactType == 'person':
                contactData = {"contact": {"name": contactName, "type": contactType},
                               "messages": [ messages ]}
                DB.append_to_contacts_df(contactData)  # add data to the data frame

            # Set as scraped
            self.scrapedContacts.append(contactName)

            # get the avatar of the contact
            if i < NUMBER_OF_CONTACT_PICTURES:
                cropped = self.__get_contact_avatar()
                if cropped is not None:
                    cropped.save(TEMP_AVATAR_PATH + str(i) + ".jpg")
                else:
                    self.defaultAvatar.save(TEMP_AVATAR_PATH + str(i) + ".jpg")

            # After we have the data we add it to scraped contacts
            scraped_contacts.append(contactName)

            # go to next chat
            self.__go_to_next_contact()

        # Set user whastapp name
        DB.set_user_whatsapp_name(self.user_whatsapp_name)

        scrapeTotalTime = time.time() - scrapeStartTime
        print("Scraper: scrape: finished. Messages and seconds: " + str(scrapeTotalMsgs) + " in " +
              str(scrapeTotalTime) + " seconds.")

    # ===================================================================
    #   Scraper helper functions
    # ===================================================================

    def __load_chat(self):
        """
        Load to page all message for current open chat.
        """
        print("Load chat")

        self.__stubborn_load_click()

        self.wait_for_element('.btn-more')
        startTime = time.time()
        while len(self.browser.execute_script("return $('.btn-more').click();")) is not 0:
            # # TODO for debugging
            if time.time() - startTime > 5:
                break
            time.sleep(0.001)
            continue

    def __get_contact_details(self):
        """
        Get contact name and type (contact/group). This is done by clicking on Chat Menu button and
        opening a submenu which contains the word Contact or Group and extracting that word.
        """
        # Get contact name
        contactName = self.wait_for_element_by_script("return $('#main h2 span').text()")
        # contactName = self.browser.execute_script("return document.getElementById("
        #                                           "'main').getElementsByTagName('h2');")[ 0 ].text

        # If this is a contact chat then this field will not appear
        if len(self.browser.execute_script("return document.getElementsByClassName('msg-group');")) \
                == 0:
            contactType = "person"
        else:
            contactType = "group"

        return contactName, contactType

    def __get_messages(self, contactType, contactName):
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
        rawMessages = self.browser.execute_script(scrapingScripts.getTextMessages())

        # Onetime update for user whatsapp name
        if self.user_whatsapp_name is None:
            outMsg = self.browser.execute_script(scrapingScripts.getSingleOutgoingMessage())
            if outMsg is not None:
                self.user_whatsapp_name, a, b = self.__parse_message(outMsg)

        # Extract data from raw message
        for msg in rawMessages:

            name, text, dateandtime = self.__parse_message(msg)

            # Unsupported message
            if name is None:
                continue

            msgData = {"name": name, "text": text, "time": dateandtime}
            messages.append(msgData)

        return messages

    def __get_group_messages(self):
        """
        Returns summary of group chat: each group member name and how many msgs they sent.
        @:return list of len 2: [int totalMessages , dict {"Asaf":360, "Neta":180,...}]
        """

        groupData = {}  # data to be returned

        rawMessages = self.browser.execute_script(scrapingScripts.getTextMessages())
        totalMessages = len(rawMessages)

        for msg in rawMessages:

            name, text, dateandtime = self.__parse_message(msg)

            # update contact if exists otherwise create
            if name in groupData:
                groupData[ name ] += 1
            else:
                groupData[ name ] = 1

        # print("getGroupMessages got " + str(len(incomingMessages)) + " messages, here they are:")
        # print(str(groupData))
        return [ totalMessages, groupData ]

    def __parse_message(self, msg):
        # Unsupported messages of type image, video, audio, etc
        if msg is None or len(msg) == 0:
            return None, None, None

        datetimeEnd = msg[0].find("]")
        dateandtime = msg[0][3:datetimeEnd]

        name = msg[0][datetimeEnd + 2:]
        nameEnd = name.find(":")
        name = name[:nameEnd]

        text = msg[0][datetimeEnd + nameEnd + 7:]

        # Unsupported messages of type emoji
        if text == "":
            return None, None, None

        return name, text, dateandtime

    def __trim_avatar(self, im):
        """
        Helper function that trims white margins from the given image
        :return:
        """
        bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        return im.crop(bbox)

    def __get_contact_avatar(self):
        """
        Sends to db the avatar of current loaded chat.
        """
        print("In getContactAvatar")

        # Getting the small image's url and switching to the large image
        avatar_url = self.wait_for_element('#main .chat-avatar img', 2)

        # If contact has no avatar
        if avatar_url is None:
            return None

        avatar_url = avatar_url.get_attribute("src")
        avatar_url = avatar_url[:34] + "l" + avatar_url[35:]

        # Opening a new tab
        self.browser.execute_script("window.open('" + avatar_url + "');")

        # Switching to the new tab and navigating to image's url
        defWin = self.browser.window_handles[0]
        newWin = self.browser.window_handles[1]
        self.browser.switch_to_window(newWin)
        self.browser.get(avatar_url)
        self.browser.execute_script(scrapingScripts.initJQuery())

        # Saving a screen shot
        img = self.wait_for_element('body img')

        # Getting image size for cropping
        width = img.get_attribute("width")
        height = img.get_attribute("height")

        self.browser.save_screenshot(TEMP_SCREENSHOT_PATH)
        # Cropping
        screenshot = Image.open("full_screen_shot_temp.png")
        cropped = screenshot.crop((0, 0, int(width), int(height)))

        # Closing the tab
        self.browser.close()
        self.browser.switch_to_window(defWin)

        return self.__trim_avatar(cropped)

    def __go_to_next_contact(self):
        """
        Goes to next contact chat in contact list. This is done by locating the "search" box and
        pressing tab and then arrow down.
        """
        actions = ActionChains(self.browser)
        actions.click(self.wait_for_element('.input.input-search')).send_keys(Keys.TAB).send_keys(
            Keys.ARROW_DOWN).perform()

    def __stubborn_load_click(self):
        print("Scraper: stubbornClick starting...")
        i = 0

        while (True):
            try:
                ActionChains(self.browser).click(
                        self.wait_for_element('#main .message-list', 1)).perform()
                print("Scraper: stubbornClick finished on iteration: " + str(i))
                return
            except StaleElementReferenceException:
                i += 1
                if i & 100 == 0:
                    ActionChains(self.browser).click(self.wait_for_element_by_script(
                            "return $('#main .message-list');")[0]).perform()
                print("Scraper: stubbornClick iteration " + str(i))
                continue

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

        return elements[ 0 ]

    def wait_for_element_by_script(self, script, timeout=10):
        """
        General helper function. Searches and waits for css element to appear on page and returns it,
        if it doesnt appear after timeout seconds prints relevant exception and returns None.
        """
        startTime = time.time()
        elements = self.browser.execute_script(script)

        while (len(elements) == 0):
            elements = self.browser.execute_script(script)
            if time.time() - startTime > timeout:
                return None

        return elements
