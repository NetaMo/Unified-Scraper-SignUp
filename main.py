import glob
import os
import sys

import time
import tornado.ioloop
import tornado.web
import WhatsAppWebScraper
from Webdriver import Webdriver
from WhatsAppDB import WhatsAppDB
import DataAnalysisTestDriver # TODO remove wehn not needed

firstTime = True
runFile = "C:\\Users\\maoze\\PycharmProjects\\Unified-Scraper-SignUp\\run.bat"

"""
run the WhatsApp web scrapper.
"""


def scrape_whatsapp():
    """
    runs the whatsapp web scrapping procedure.
    :param db: the WhatsAppDB object
    """
    # print("create driver")
    driver = Webdriver()  # create new driver
    scraper = WhatsAppWebScraper.WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    scraper.scrape(DB)  # scrape
    print("finished scraping,load headset instructions")
    driver.close()  # close driver


def InitializeDBAndAvatars():
    """
    Initialize a new DB instance,
    and remove all avatars
    """
    print("InitializeDBAndAvatars")
    global DB  # TODO
    DB = WhatsAppDB()
    files = glob.glob('static/tempAvatars/*')
    for f in files:
        if 'contact_avatar' in f:
            os.remove(f)


"""""
web page handlers:
"""""


class IphoneHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 6: Iphone Chosen")
        DB.phone = "ios"
        self.finish()


class AndroidHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 6: Android Chosen")
        DB.phone = "android"
        self.finish()


class LandingHandler(tornado.web.RequestHandler):
    def get(self):
        print("Stage 1: Loading HomePage")
        self.render("LandingPage.html")


class NameSubmitHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 3: Name Submitted, Loading TermsPage")
        # These variables hold the users input
        first_name = self.get_argument("first")
        last_name = self.get_argument("last")
        print("User first name:", first_name)
        print("User last name:", last_name)

        # assign the first name to the user name attribute in DB
        DB.user_name = first_name
        DB.user_first_name = first_name
        DB.user_last_name = last_name

        # writes the users name to file
        with open('users', 'a', encoding='utf8') as users_file:
            users_file.write(first_name + " " + last_name + "\n")

        self.finish()


class NickNameSubmitHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 2: Nick Name Submitted, Loading Full Name")
        # These variables hold the users input
        nick_name = self.get_argument("nick")
        print("User NickName:", nick_name)
        self.finish()
        DB.user_nicknames.append(nick_name)


class TermAgreeHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 4: Agreed, Loading WhatssApp web scrapper")
        # run whats up web scrapper
        print("Stage 4: Agreed, Go to phone sort")
        self.finish()


class ChoosePhoneHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 5: Load Phone Sort")
        phone = self.get_argument("phone")
        DB.phone = phone
        print('Phone is {}'.format(phone))
        self.finish()

class ResetBrowserHandler(tornado.web.RequestHandler):

    def get(self):
        mainDriver.close()
        exit(0)
        self.finish()


class LetsGoHandler(tornado.web.RequestHandler):

    def get(self):

        print("Stage 7: Lets GO!, Load whatssapp web!")
        # Insert whats up web run here
        scrape_whatsapp()

        # if mainDriver is not None:
        #     mainDriver.getBrowser().get("localhost:8888/static/headset2.html")
        # mainDriver.getBrowser().refresh()

        # analyze and Save the results
        DB.run_data_analysis_and_store_results()

        DataAnalysisTestDriver.test_data_analysis(DB)
        print("going out of handler letsGo")
        self.finish()


"""
unity communication handlers
"""


class GiveLatestChatsHandler(tornado.web.RequestHandler):

    def get(self):
        print("GetLatestChatsHandler")
        self.finish(DB.latest_chats)


class GiveClosestPersonsAndMsgs(tornado.web.RequestHandler):

    def get(self):
        print("GetClosestPersonsAndMsgs")
        self.finish(DB.closest_persons_and_msg)


class HaveHebrew(tornado.web.RequestHandler):

    def get(self):
        print("HaveHebrew")
        self.finish(DB.have_hebrew)


class GiveGoodNightMessages(tornado.web.RequestHandler):
    def get(self):
        print("GiveGoodNightMessages")
        self.finish(DB.good_night_messages)


class GiveDreamsOrOldMessages(tornado.web.RequestHandler):

    def get(self):
        print("GiveDreamsOrOldMessages")
        self.finish(DB.dreams_or_old_messages)


class GiveMostActiveGroupsAndUserGroups(tornado.web.RequestHandler):

    def get(self):
        print("GiveMostActiveGroupsAndUserGroups")
        self.finish(DB.most_active_groups_and_user_groups)


class GiveChatArchive(tornado.web.RequestHandler):

    def get(self):
        print("GiveChatArchive")
        self.finish(DB.chat_archive)


class ResetHandler(tornado.web.RequestHandler):
    """
    Sends the user to the first page, resets the DB and removes all avatars
    """
    def get(self):
        print("ResetHandler")
        InitializeDBAndAvatars()
        try:
            mainDriver.getBrowser().execute_async_script('''
            setTimeout(function(){
                window.location = '/static/reset.html';
            }, 1000);
            ''')
        except Exception as e:
            print(e)

        self.finish()


"""""
make_app, settings, main
"""""

# Allows access to static directory to any http request
settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))


# Create tornado web application
def make_app():
    # print("make_app")
    return tornado.web.Application([(
        # web page handlers
        (r"/", LandingHandler)),
        (r"/namesubmit", NameSubmitHandler),
        (r"/agree", TermAgreeHandler),
        (r"/nicknamesubmit", NickNameSubmitHandler),
        (r"/choosephone", ChoosePhoneHandler),
        (r"/letsgo", LetsGoHandler),
        (r"/resetBrowser", ResetBrowserHandler),
        # unity handlers
        (r"/get_latest_chats", GiveLatestChatsHandler),
        (r"/get_closest_persons_and_msgs", GiveClosestPersonsAndMsgs),
        (r"/have_hebrew", HaveHebrew),
        (r"/get_good_night_messages", GiveGoodNightMessages),
        (r"/get_dreams_or_old_messages", GiveDreamsOrOldMessages),
        (r"/get_most_active_groups_and_user_groups", GiveMostActiveGroupsAndUserGroups),
        (r"/get_chat_archive", GiveChatArchive),
        (r"/reset", ResetHandler)
    ], **settings)

# Initialize and empty DB variable for future use
DB = None

# Initialize an empty driver for the user.
# We'll use this to send the user back to the main page when we reset the experience
driver_user = None



if __name__ == "__main__":
    InitializeDBAndAvatars()
    global mainDriver

    port = 8888
    app = make_app()

    # enter webPage as the first argument to run the web page
    if sys.argv[1] == 'WebPage':
        print("web Page")
        # A Chrome window to navigate to our site

        mainDriver = Webdriver()
        mainDriver.browser.get("localhost:" + str(port))

    # save the data to a file for future work
    elif sys.argv[1] == 'SaveData':
        print("scrapping and saving data to pickle")
        scrape_whatsapp()

        DB.save_db_to_files(".\\stored data\\")
        sys.exit()

    # load the last stored data and analyze it
    elif sys.argv[1] == 'LoadData':
        print('loading the data')
        DB.load_db_from_files(".\\stored data\\")

        # analyze and Save the results
        DB.run_data_analysis_and_store_results()

        # Print data
        DataAnalysisTestDriver.test_data_analysis(DB)


    # just runs the scrapping and analysis
    else:
        print("scrape_whatsapp")
        scrape_whatsapp()

        # analyze and Save the results
        DB.run_data_analysis_and_store_results()

        # Print data
        DataAnalysisTestDriver.test_data_analysis(DB)

        print("server keeps running for unity get requests")

    print("listening")
    app.listen(port)

    # app.listen(port, address="192.16873.1")  # listen to ip

    tornado.ioloop.IOLoop.current().start()

    # lt.join()
