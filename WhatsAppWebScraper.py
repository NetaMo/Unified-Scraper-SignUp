import codecs
import re
import string
import time
from datetime import datetime

from PIL import Image, ImageChops
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import ScrapingScripts as scrapingScripts
from Webdriver import Webdriver


# ===================================================================
# Scraper class
# ===================================================================
class WhatsAppWebScraper:
    """
    Main class for scraping whatsapp. Receives open browser, goes to WhatsApp Web page, scrapes data
    and sends one contact at a time to the server.
    """
    # Server data
    SERVER_POST_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    # how much person contact profile images to save
    NUMBER_OF_PERSON_CONTACT_PICTURES = 6

    # Where to save temporary images for avatars
    TEMP_AVATAR_PATH = "static/tempAvatars/contact_avatar"
    TEMP_SCREENSHOT_PATH = "full_screen_shot_temp.png"

    # Total time for the chat scraper
    RUNNING_TIME = 300

    # How much time of the RUNNING_TIME we will dedicate for persons
    FRACTION_PERSON = 0.9

    # Maximum groups and persons we want
    MAX_GROUPS = 6
    MAX_PERSONS = 6

    # Maximum time tha scraper keep clicking load more and get more messages
    MIN_TIME_NEEDED_TO_GET_ENOUGH_CONTACTS = int(RUNNING_TIME / NUMBER_OF_PERSON_CONTACT_PICTURES)
    MAX_PERSON_LOAD_CHAT = min(int(RUNNING_TIME * FRACTION_PERSON / MAX_PERSONS),
                               MIN_TIME_NEEDED_TO_GET_ENOUGH_CONTACTS)
    MAX_GROUP_LOAD_CHAT = min(int(RUNNING_TIME * (1 - FRACTION_PERSON) / MAX_GROUPS),
                              MIN_TIME_NEEDED_TO_GET_ENOUGH_CONTACTS)

    # Rank parameters
    LONG_MESSAGE = 40  # Define what does it mean long message (length of one message)
    LONG_DAY = 80  # Define what does it mean long day (count of messages in one day)
    THRESHOLD_RANK = 0.16  # Define the min rank, above this rank the scraper will scrape the contact for longer
    GOOD_RANK_ADDITIONAL_SECONDS = 200  # If the contact is above rank, how many seconds we add for him

    # set of the interesting words for the dynamic chat loading
    interesting_words = set(codecs.open('bag of words', encoding='utf-8').read().split())

    def __init__(self, webdriver):
        self.browser = Webdriver.getBrowser(webdriver)  # Get browser
        self.browser.set_page_load_timeout(150)  # Set timeout to 150 seconds
        self.browser.get("https://web.whatsapp.com/")  # Navigate browser to WhatsApp page
        self.browser.execute_script(scrapingScripts.initJQuery())  # active the jquery lib
        self.scrapedContacts = [ ]  # List of scraped contacts
        self.defaultAvatar = Image.open("defaultAvatar.jpg")
        self.user_whatsapp_name = None  # what is the user's whatsapp outgoing messages name
        # How many contact we scraped already
        self.person_count = 0
        self.group_count = 0

        self.probably_hebrew_interface = True

        # Wait in current page for user to log in using barcode scan.
        self.wait_for_element('.infinite-list-viewport', 300)

        # Move browser out of screen scope
        # We don't want to resize the window, otherwise avatars don't work
        # self.browser.set_window_position(-999999, 999999)

    # ===================================================================
    #   Main scraper function
    # ===================================================================

    def scrape(self, DB):
        time.sleep(3)

        print("... Scraper starting...")
        scrapeStartTime, scrapeTotalMsgs = time.time(), 0

        # Get to first contact chat
        actions = ActionChains(self.browser)  # init actions option (click, send keyboard keys, etc)
        try:
            actions.click(self.wait_for_element('.input.input-search')).send_keys(Keys.TAB).perform()
        except StaleElementReferenceException:
            # Element is removed from the DOM structure, that happens when whatsapp refresh
            # the page and we don't want to break the app. I'm retying again after 2 sec.
            time.sleep(3)
            actions.click(self.wait_for_element('.input.input-search')).send_keys(Keys.TAB).perform()

        # We want to scrape just NUMBER_OF_CONTACT_PICTURES
        avatar_count = 0

        # Init contact name, type and msgs (so we can use them even if first contact has error)
        contact_name, contact_type, messages = None, None, None

        # Scrape each chat
        running_time_start = time.time()

        # Iterate over the contacts until we reach our RUNNING_TIME
        while time.time() - running_time_start < self.RUNNING_TIME:
            contact_iteration_start = time.time()
            try:
                # load all conversations for current open chat
                contact_name, contact_type, messages = self._load_chat()

                # If we scraped enough of this contact load chat will return None-s
                if (contact_name, contact_type, messages) == (None, None, None):
                    print("...... Already scraped enough contacts of type", contact_type, "sorry",
                          contact_name)
                    self._go_to_next_contact()
                    continue
            except Exception as e:  # We had unknown error, we want to go to the next contact
                print("### Fault redundancy ### Contact failed for unknown reason, going to next "
                      "contact. Hug yourself and debug. Details:",
                      contact_name,
                      contact_type,
                      messages)
                self._go_to_next_contact()
                continue
            # except Exception as e:  # We had unknown error, we want to go to the next contact
            #     print("### Fault redundancy ### Contact failed for unknown reason, going to next "
            #           "contact. Hug yourself and debug. Details:",
            #           contact_name,
            #           contact_type,
            #           messages)
            #     self._go_to_next_contact()
            #     continue

            # If the user received message while scraping we don't want to scrape it again
            if contact_name in self.scrapedContacts:
                print('this contact is scraped', contact_name)
                self._go_to_next_contact()
                continue

            # Check if we already have enough of this contactType
            if not self._check_max_persons_groups(contact_type):
                print('max persons', contact_name, contact_type)
                self._go_to_next_contact()
                continue

            # Initialize data item to store chat
            contact_scrape_time = time.time() - contact_iteration_start
            if contact_type == 'group':
                contactData = {
                    "contactName": contact_name,
                    "contactMessageTotal": messages[ 0 ],
                    "contactMessageCounter": messages[ 1 ],
                }
                DB.append_to_groups_df(contactData)
                self.group_count += 1
                print("...... Got " + str(messages[0]) + " messages in " + str(
                        round(contact_scrape_time, 3)) + " for " + str(contact_name))
                scrapeTotalMsgs += messages[0]

            elif contact_type == 'person':
                contactData = {
                    "contact": {
                        "name": contact_name,
                        "type": contact_type
                    },
                    "messages": [ messages ],
                }

                # add data to the data frame
                DB.append_to_contacts_df(contactData)
                self.person_count += 1
                # print data
                print("...... Got " + str(len(messages)) + " messages in " + str(round(
                        contact_scrape_time, 3)) + " for contact " + str(contact_name))
                scrapeTotalMsgs += len(messages)

                # get the avatar of the first X persons
                if avatar_count < self.NUMBER_OF_PERSON_CONTACT_PICTURES:
                    cropped = self._get_contact_avatar()
                    if cropped is not None:
                        cropped.save(self.TEMP_AVATAR_PATH + str(avatar_count) + ".jpg")
                    else:
                        self.defaultAvatar.save(self.TEMP_AVATAR_PATH + str(avatar_count) + ".jpg")
                avatar_count += 1

            # Set as scraped
            self.scrapedContacts.append(contact_name)

            # go to next chat
            self._go_to_next_contact()

        # Set user whastapp name
        DB.set_user_whatsapp_name(self.user_whatsapp_name)

        scrapeTotalTime = time.time() - scrapeStartTime
        print("... Scraper finished. Got " + str(scrapeTotalMsgs) + " messages in " +
              str(scrapeTotalTime) + " seconds, at a rate of " + str(round(
                scrapeTotalMsgs / scrapeTotalTime, 3)) + " messages/second.\n")

    # ===================================================================
    #   Scraper helper functions
    # ===================================================================

    def _load_chat(self):
        """
        Load to page all message for current open chat.
        """

        self._stubborn_load_click()

        self.wait_for_element('.btn-more')

        # Get contact name and type (person/group).
        contactName, contactType = self._get_contact_details()

        # Check if we already have enough of this contactType
        if not self._check_max_persons_groups(contactType):
            return None, None, None

        # How long we should keep clicking "Load More"
        max_load_chat_time = self._get_max_load_chat_time(contactType)

        # Get messages from current chat
        messages = self._get_messages(contactType, contactName)

        # Check contact rank
        if contactType == 'person':
            rank = self._get_rank(messages)
            if rank > self.THRESHOLD_RANK:
                max_load_chat_time += self.GOOD_RANK_ADDITIONAL_SECONDS
                print("...... The next contact is interesting... scraping more nom nom.")
            print("...... The next contact's rank is", round(rank, 3))

        startTime = time.time()
        while self.browser.execute_script("return $('.btn-more').click();"):
            if time.time() - startTime > max_load_chat_time:
                break
            time.sleep(0.001)

        messages = self._get_messages(contactType, contactName)

        return self.clean_hidden_chars(contactName), self.clean_hidden_chars(contactType), messages

    def _get_contact_details(self):
        """
        Get contact name and type (contact/group). This is done by clicking on Chat Menu button and
        opening a submenu which contains the word Contact or Group and extracting that word.
        """
        # It takes around 100 ms to switch the title of the contact name,
        # so wait 200 to ensure it switch's the contact name,
        # Otherwise we get the contact name of the previous contact and all hell breaks loose
        time.sleep(0.2)

        # Get contact name
        contactName = self.wait_for_element_by_script("return $('#main h2 span').text()")
        contactName = self.clean_hidden_chars(contactName)

        # If this is a contact chat then this field will not appear
        is_group = self.wait_for_element_by_script("return document.getElementsByClassName('msg-group');", 2)

        return contactName, "group" if is_group else "person"

    def _get_messages(self, contactType, contactName):
        """
        Given a chat with a contact, return all messages formatted to be sent to server.
        """

        # Group chat case
        if contactType == 'group':
            return self._get_group_messages()
        # Person chat case
        return self._get_person_messages()

    def _get_person_messages(self):
        """
        Get all messages from current open chat, parse to fields name, datetime and text.
        :return: list of messages [{"name":name, "text": text, "time":time}, {"name":name,
        "text": text, "time":time}, ...]
        """
        messages = []
        rawMessages = self.browser.execute_script(scrapingScripts.getTextMessages())

        # Onetime update for user whatsapp name
        if self.user_whatsapp_name is None:
            outMsg = self.browser.execute_script(scrapingScripts.getSingleOutgoingMessage())
            if outMsg is not None:
                self.user_whatsapp_name = outMsg[outMsg.find("\xa0")+1: outMsg.find("\xa0", outMsg.find("\xa0")+2)-1]
        # Extract data from raw message
        for msg in rawMessages:

            name, text, dateandtime = self._parse_message(msg)

            # Unsupported message
            if name is None:
                continue

            msgData = {"name": name, "text": text, "time": dateandtime}
            messages.append(msgData)

        return messages

    def _get_group_messages(self):
        """
        Returns summary of group chat: each group member name and how many msgs they sent.
        @:return list of len 2: [int totalMessages , dict {"Asaf":360, "Neta":180,...}]
        """

        groupData = {}  # data to be returned

        rawMessages = self.browser.execute_script(scrapingScripts.getTextMessages())
        totalMessages = len(rawMessages)

        for msg in rawMessages:

            name, text, dateandtime = self._parse_message(msg)

            # In case of images
            if name is None:
                continue

            # update contact if exists otherwise create
            if name in groupData:
                groupData[ name ] += 1
            else:
                groupData[ name ] = 1

        return [ totalMessages, groupData ]

    def _parse_message(self, msgRaw):
        try:
            # Unsupported messages of type image, video, audio, etc
            if msgRaw is None or len(msgRaw) == 0:
                return None, None, None

            msg = self.clean_hidden_chars(msgRaw[0])

            datetimeEnd = msg.find("]")
            datetimeStart = msg.find("[")
            dateandtime = msg[datetimeStart + 1:datetimeEnd]

            name = msg[datetimeEnd + 2:]
            nameEnd = name.find(":")
            name = name[1:nameEnd]

            text = msg[datetimeEnd + nameEnd + 7:]

            # Unsupported messages of type emoji
            if text == "":
                return None, None, None
        except:  # In case we had new format we don't support
            return None, None, None

        return name, text, dateandtime

    @staticmethod
    def _trim_avatar(im):
        """
        Helper function that trims white margins from the given image
        :return:
        """
        try:
            bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
            diff = ImageChops.difference(im, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
            return im.crop(bbox)
        except IndexError:
            print("DEBUGGING: Failed in _trim_avatr on image: ", im)
            return im

    def _get_contact_avatar(self):
        """
        Sends to db the avatar of current loaded chat.
        """
        # print("In getContactAvatar")

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

        self.browser.save_screenshot(self.TEMP_SCREENSHOT_PATH)
        # Cropping
        screenshot = Image.open("full_screen_shot_temp.png")
        cropped = screenshot.crop((0, 0, int(width), int(height)))

        # Closing the tab
        self.browser.close()
        self.browser.switch_to_window(defWin)

        return self._trim_avatar(cropped)

    def _go_to_next_contact(self):
        """
        Goes to next contact chat in contact list. This is done by locating the "search" box and
        pressing tab and then arrow down.
        """
        actions = ActionChains(self.browser)
        try:
            actions.click(self.wait_for_element('.input.input-search')).send_keys(Keys.TAB).send_keys(
                Keys.ARROW_DOWN).perform()
        except StaleElementReferenceException:
            # Element is removed from the DOM structure, that happens when whatsapp refresh
            # the page and we don't want to break the app. I'm retying again after 2 sec.
            time.sleep(3)

            actions.click(self.wait_for_element('.input.input-search')).send_keys(Keys.TAB).send_keys(
                Keys.ARROW_DOWN).perform()

    def _stubborn_load_click(self):
        # print("Scraper: stubbornClick starting...")
        i = 0

        while (True):
            try:
                ActionChains(self.browser).click(
                    self.wait_for_element('#main .pane-chat-empty', 1)).perform()
                # print("Scraper: stubbornClick finished on iteration: " + str(i))
                return
            except StaleElementReferenceException:
                i += 1
                if i & 100 == 0:
                    ActionChains(self.browser).click(self.wait_for_element_by_script(
                        "return $('#main .message-list');")[0]).perform()
                # print("Scraper: stubbornClick iteration " + str(i))
                continue

    def _get_max_load_chat_time(self, contentType):
        """
        Returns the maximum time for load chat, also checks if it's group or person
        and calculate different times.
        """
        return self.MAX_PERSON_LOAD_CHAT if contentType == "person" else self.MAX_GROUP_LOAD_CHAT

    def _check_max_persons_groups(self, contactType):
        """
        Checks if we have reached the quantity of persons/groups we want
        according to MAX_PERSONS/MAX_GROUPS.
        Returns True if we want this contactType, False otherwise.
        """
        if contactType == "person":
            return self.person_count < self.MAX_PERSONS
        return self.group_count < self.MAX_GROUPS

    @staticmethod
    def clean_hidden_chars(s):
        '''
        Removing unwanted characters from strings
        :param s: string to clean
        :return: string
        '''
        hiddens = ["\\xa0", " \\xa0", "\\u2060", "null"]  # In case we find more of them
        for hidden in hiddens:
            s = s.replace(hidden, "")
        return s

    def _get_rank(self, messages):
        """
        Ranks each person so we can sort them by relevant
        """
        long_messages_count = 0
        bag_of_words = set()

        # Remove all unnecessary chars like !@#%~.
        pattern = re.compile('[%s]' % re.escape(string.punctuation))

        for message in messages:
            if len(message['text']) > self.LONG_MESSAGE:
                long_messages_count += 1

            words_list = pattern.sub('', message['text']).split()

            # Add to the set, no duplicates
            bag_of_words.update(words_list)

        # Find the avg messages per day ''
        date_start = datetime.strptime(messages[0]['time'], '%H:%M %m/%d/%Y')
        date_end = datetime.strptime(messages[-1]['time'], '%H:%M %m/%d/%Y')
        days_count = (date_end - date_start).days

        # Final data we will use to calculate the rank
        long_messages_rank = long_messages_count / len(messages)
        bag_rank = self.bag_rank(bag_of_words)
        avg_messages_per_day = (days_count / len(messages)) / self.LONG_DAY

        # Best mathematical solution for this problem, is to normalize(0<x<1) the data and then find the average
        return (long_messages_rank + bag_rank + avg_messages_per_day) / 3

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
            time.sleep(0.001)

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

    def _get_rank(self, messages):
        """
        Ranks each person so we can sort them by relevant
        """

        if len(messages) == 0:
            return 0.001

        long_messages_count = 0
        bag_of_words = set()

        # Remove all unnecessary chars like !@#%~.
        pattern = re.compile('[%s]' % re.escape(string.punctuation))

        for message in messages:
            if len(message['text']) > self.LONG_MESSAGE:
                long_messages_count += 1

            words_list = pattern.sub('', message['text']).split()

            # Add to the set, no duplicates
            bag_of_words.update(words_list)

        # Find the avg messages per day ''
        date_start = datetime.strptime(messages[0]['time'], '%H:%M %m/%d/%Y')
        date_end = datetime.strptime(messages[-1]['time'], '%H:%M %m/%d/%Y')
        days_count = (date_end - date_start).days

        # Final data we will use to calculate the rank
        long_messages_rank = long_messages_count / len(messages)
        bag_rank = self.bag_rank(bag_of_words)
        avg_messages_per_day = (days_count / len(messages)) / self.LONG_DAY

        # Best mathematical solution for this problem, is to normalize(0<x<1) the data and then find the average
        return (long_messages_rank + bag_rank + avg_messages_per_day) / 3

    def bag_rank(self, bag_of_words):
        """"
        Returns the rank of the bag_of_ words set object.
        float number between 0 to 1
        """

        # Find how many words has intersection with the super duper words
        interesting_words_super = {"חלמתי", "חלומות", "חלמת", "dream", "dreamt", "dreaming", "dreams", "rêver", "rêves", "rêvé", "rêve",
                                   "reve", "reves", "rever", "dreamed", "good night", "לילה טוב", "bonne nuit", "sweet dreams"}
        intersection_count_super = len(interesting_words_super.intersection(bag_of_words))

        # If we found any super duper word, return 999 as a rank
        if intersection_count_super:
            print("found a super interesting word- loading more")
            return 999

        # Find how many words has intersection with the interesting words
        intersection_count = len(self.interesting_words.intersection(bag_of_words))
        print("...... the intersection count with the bag of words is :" + str(intersection_count))

        # Normalize
        return intersection_count/len(bag_of_words)


