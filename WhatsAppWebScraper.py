# from PIL import Image
import time
import datetime
from Webdriver import Webdriver
from selenium.common.exceptions import TimeoutException, \
    StaleElementReferenceException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as ec
from selenium.webdriver.common.keys import Keys

# ===================================================================
# Global variables
# ===================================================================
# Server data
SERVER_URL_CHAT = "http://localhost:8888/chat"
SERVER_URL_FINISHED = "http://localhost:8888/chatFinished"
SERVER_POST_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# Days of the week
WEEKDAYS = ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY')
# how much profile images to save
NUMBER_OF_CONTACT_PICTURES = 6

# todo move to scripts
# add jquery
with open("jquery-2.2.3.min.js", 'r') as jquery_js:
    jquery = jquery_js.read()  # read the jquery from a file


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

        # Conversation table from day names to date for past week
        self.dayNamesToDates = self.get_day_names_to_dates()
        
        # Wait in current page for user to log in using barcode scan.
        self.wait_for_element(".infinite-list-viewport", 300)
        # self.browser.set_window_size(0, 0)
        # self.browser.set_window_position(-800, 600)

        self.browser.execute_script(jquery)  # active the jquery lib

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
        for i in range(1, 2):

            loadStartTime = time.time()
            chat = self.load_chat()  # load all conversations for current open chat
            print("Loaded chat in " + str(time.time() - loadStartTime) + "seconds")

            # Get contact name and type (person/group).
            contactName, contactType = self.get_contact_details(actions)

            # Initialize data item to store messages
            contactData = {"contact": {"name":contactName,"type":contactType},"messages":[]}

            # Get messages from current chat
            print("Get messages for: " + str(contactName))
            startTime = time.time()
            messages = self.get_messages(chat, contactType, contactName)
            totalMsgTime = time.time() - startTime
            contactData['messages'].append(messages)
            print("Got " + str(len(messages)) + " messages in " + str(totalMsgTime))

            # get the avatar of the contact TODO change to apply only the first six contacts
            # if i < NUMBER_OF_CONTACT_PICTURES:
            #     self.get_contact_avatar()

            # add data to the data frame
            DB.append_to_contacts_df(contactData)
            # requests.post(SERVER_URL_CHAT, json=contactData, headers=SERVER_POST_HEADERS)

            # go to next chat
            self.go_to_next_contact()

        print("done scraping")

        # send finished signal to server
        # requests.post(SERVER_URL_FINISHED, json={}, headers=SERVER_POST_HEADERS)

# ===================================================================
#   Scraper helper functions
# ===================================================================

    def load_chat(self):
        """
        Load to page all message for current open chat.
        """
        print("Load chat")

        actions = ActionChains(self.browser)  # init actions
        chat = self.wait_for_element(".message-list")  # wait for chat to load
        actions.click(chat).perform()

        # ----------a new faster way to load chats---------------------
        # load the chat using javascript code.
        iterations = 0
        while len(self.browser.execute_script("return $('.btn-more').click();")) is not 0:
            if iterations % 10 is 0: # TODO check what is the optimal parameter
                self.browser.execute_script("$(\"#pane-side\").animate({scrollTop:  0});")
            iterations += 1


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

    def get_contact_details(self, actions):
        """
        Get contact name and type (contact/group). This is done by clicking on Chat Menu button and
        opening a submenu which contains the word Contact or Group and extracting that word.
        """
        # Get contact name
        # TODO make this selector less specific to match possible page variations
        contactName = self.browser.find_element_by_css_selector("#main header div.chat-body "
                                                                "div.chat-main h2 span").text

        # If this is a contact chat then this field will not appear
        if self.get_elemenet(".msg-group") == None:
            contactType = "person"
        else:
            contactType = "group"

        return contactName, contactType

    def get_messages(self, chat, contactType, contactName):
        """
        Given a chat with a contact, return all messages formatted to be sent to server.
        """

        # Group chat case
        if contactType == 'group':
            return self.get_group_messages(chat)

        messageElements = self.wait_for_element(".msg", 10, None, False)
        messages = []
        name, text, time = None, None, None
        lastName, lastDay = contactName, "1/1/2000" # TODO validate with server API

        for msg in messageElements:

            # Incoming/Outgoing message
            textContainer = self.get_elemenet(".selectable-text", msg)
            if textContainer is not None:
                # Get text and time
                text = textContainer.text
                time = msg.find_element_by_css_selector(".message-datetime").text + ", " + lastDay

                # Incoming message case
                if self.get_elemenet(".message-in", msg):
                    if contactType == 'person':
                        name = contactName
                    else:
                        name = self.get_elemenet(".message-author", msg)
                        if name is None:
                            name = lastName
                        else:
                            name = str(name.text).replace("\u2060","")
                            lastName = name

                # Outgoing message case
                elif self.get_elemenet(".message-out", msg) is not None:
                    name = "Me" # TODO validate with server API

                # Add message to message list
                msgData = {"name":name, "text": text, "time":time}
                messages.append(msgData)
                # print(msgData) # Print each message

            # System date message
            elif self.get_elemenet(".message-system", msg) is not None:
                # Unsupported system message
                if not msg.text:
                    continue
                # If it is a date or a weekday name
                if (len(msg.text) > 13 and msg.text[-10] == '/'):
                    lastDay = str(msg.text).replace("\u2060","")
                elif str(msg.text).replace("\u2060", "") in self.dayNamesToDates:
                    lastDay = self.dayNamesToDates[str(msg.text).replace("\u2060", "")]

            # Unsupported message type (image, video, audio...), we do not return these.
            else:
                continue

        return messages

    def get_group_messages(self, chat):
        """
        Returns summary of group chat: each group member name and how many msgs they sent.
        @:return dictionary {"Asaf":360, "Neta":180,...}
        """

        groupData = {} # data to be returned
        lastName = None # last known name to send a msg, used for msgs without author name

        # Get all incoming messages, only the author name and text.
        # this script looks for class "message-in" then "emojitext" then takes .innerText
        incomingMessages = self.browser.execute_script("var B = []; var A = document.getElementsByClassName('message-in');  for (var i = 0; i < A.length; i++){ var b = []; var a = A[i].getElementsByClassName('emojitext');  for (var j = 0; j < a.length; j++){  b.push( a[j].innerText); }  B.push(b); };;return B")

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

        print("getGroupMessages got " + str(len(incomingMessages)) + " messages, here they are:")
        print(str(groupData))
        return groupData

    def get_day_names_to_dates(self):
        """
        Helper function to getMessages.
        Take care of cases where WhatsApp chat tells the date by day name, see examples below.
        The function does a one time convertion of last week day names to date.
        """
        def getDateFromDayName(weekday):
            daysBack = (datetime.date.today().isoweekday() - weekday) % 7
            return datetime.date.fromordinal(datetime.date.today().toordinal()- daysBack).strftime("%m/%d/%Y")


        return {"TODAY":datetime.date.today().strftime("%m/%d/%Y"),
                  "YESTERDAY":datetime.date.fromordinal(datetime.date.today().toordinal()- 1).strftime("%m/%d/%Y"),
                  "SUNDAY":getDateFromDayName(0),
                  "MONDAY":getDateFromDayName(1),
                  "TUESDAY":getDateFromDayName(2),
                  "WEDNESDAY":getDateFromDayName(3),
                  "THURSDAY":getDateFromDayName(4),
                  "FRIDAY":getDateFromDayName(5),
                  "SATURDAY":getDateFromDayName(6)}

    def get_contact_avatar(self):
        """
        Sends to db the avatar of current loaded chat.
        """
        print("In getContactAvatar")
        # Getting the small image's url and switching to the large image
        avatar_url = self.get_elemenet("#main header div.chat-avatar div img").get_attribute("src")
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
        self.wait_for_element("body img")

        # Getting image size for cropping
        width = self.get_elemenet("body img").get_attribute("width")
        height = self.get_elemenet("body img").get_attribute("height")
        self.browser.save_screenshot("full_screen_shot_temp.png")

        # Cropping
        screenshot = Image.open("full_screen_shot_temp.png")
        cropped = screenshot.crop((0, 0, int(width), int(height)))
        cropped.save("contact_avatar.jpg")

        # Closing the tab
        actions.send_keys(Keys.CONTROL).send_keys('w').perform()
        self.browser.switch_to_window(defWin)

    def go_to_next_contact(self, isFirst = False):
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
            elements = WebDriverWait(cssContainer, timeout).\
                until(ec.presence_of_all_elements_located((By.CSS_SELECTOR,cssSelector)))
            # print("Done waiting for element: " + cssSelector)
            if singleElement:
                return elements[0]
            return elements
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            print("Exception for element "+str(cssSelector)+" on page: "+str(self.browser.current_url))
            return None

    def get_elemenet(self, cssSelector, cssContainer = None):
        """
        Helper function. Searches for element by css selector, if it doesn't exists catchs
        NoSuchElementException and returns None.
        """
        if cssContainer is None:
            cssContainer = self.browser
        try:
            return cssContainer.find_element_by_css_selector(cssSelector)
        except (NoSuchElementException, StaleElementReferenceException):
            return None