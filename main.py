import sys
import os
from Webdriver import Webdriver
import WhatsAppWebScraper
import tornado.ioloop
import tornado.web
from WhatsAppDB import WhatsAppDB
import pandas

"""
run the WhatsApp web scrapper.
"""
# A Chrome window to navigate to our site
driver1 = Webdriver()
driver1.browser.get("localhost:8888")


def scrape_whatsapp(db):
    """
    runs the whatsapp web scrapping procedure.
    :param db: the WhatsAppDB object
    """
    driver = Webdriver()  # create new driver
    # window_before = driver.browser.window_handles[0]
    window_after = driver.getBrowser().window_handles[0]
    driver.getBrowser().switch_to.window(window_after)
    scraper = WhatsAppWebScraper.WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    print("before scrape")
    scraper.scrape(db)  # scrape
    print("after scrape")
    # TODO for debugging, delete
    while(True):
        continue
    driver.close()  # close driver


"""""
web page handlers:
"""""


class LandingHandler(tornado.web.RequestHandler):
    def get(self):
        print("Stage 1: Loading HomePage")
        self.render("LandingPage.html")


class NameSubmitHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("Stage 3: Name Submittted, Loading TermsPage")
        # These variables hold the users input
        first_name = self.get_argument("first")
        last_name = self.get_argument("last")
        print("User first name:", first_name)
        print("User last name:", last_name)

        # assign the first name to the user name attribute in DB
        self.db.user_name = first_name

        # writes the users name to file
        with open('users', 'a', encoding='utf8') as users_file:
            users_file.write(first_name + " " + last_name + "\n")


class NickNameSubmitHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("Stage 2: Nick Name Submittted, Loading Full Name")
        # These variables hold the users input
        nickName = self.get_argument("nick")
        print("User NickName:", nickName)
        #TODO Store nick name


class TermAgreeHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 4: Agreed, Loading WhatssApp web scrapper")
        # run whats up web scrapper
        scrape_whatsapp(self.db)
        print("Stage 4: Agreed, Go to phone sort")

class PhoneSortHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 5: Load Phone Sort")


class LetsGoHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("Stage 7: Lets Fucking GO!, Load whatssapp web!")
        # Insert whats up web run here
        scrape_whatsapp(self.db)

        DB.convert_to_datetime_and_sort()
        import DataAnalysisTestDriver
        DataAnalysisTestDriver.test_data_analysis(DB)

        DB.run_data_analysis_and_store_results()

"""
unity communication handlers
"""


class GiveLatestChatsHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("GetLatestChatsHandler")
        self.finish(self.db.latest_chats)


class GiveClosestPersonsAndMsgs(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("GetClosestPersonsAndMsgs")
        self.finish(self.db.closest_persons_and_msg)

class HaveHebrew(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("HaveHebrew")
        self.finish(self.db.have_hebrew)

class GiveGoodNightMessages(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("GiveGoodNightMessages")
        self.finish(self.db.good_night_messages)

class GiveDreamsOrOldMessages(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("GiveDreamsOrOldMessages")
        self.finish(self.db.dreams_or_old_messages)

class GiveMostActiveGroupsAndUserGroups(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("GiveMostActiveGroupsAndUserGroups")
        self.finish(self.db.most_active_groups_and_user_groups)

class GiveChatArchive(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("GiveChatArchive")
        self.finish(self.db.chat_archive)


"""""
make_app, settings, main
"""""

settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))



class IphoneHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 6: Iphone Chosen")


class AndroidHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 4: Agreed, Load whatssapp web")
        # Insert whats up web run here
        # isTyping()

def make_app(db):
    print("make_app")
    return tornado.web.Application([(
        # web page handlers
        (r"/", LandingHandler)),
        (r"/agree", TermAgreeHandler),
        (r"/namesubmit", NameSubmitHandler, dict(db=DB)),
        (r"/", LandingHandler),
        (r"/agree", TermAgreeHandler),
        (r"/nicknamesubmit", NickNameSubmitHandler, dict(db=DB)),
        (r"/phonesort", PhoneSortHandler),
        (r"/iphone", IphoneHandler),
        (r"/android", AndroidHandler),
        (r"/letsgo", LetsGoHandler, dict(db=DB)),
        # unity handlers
        (r"/get_latest_chats", GiveLatestChatsHandler, dict(db=DB)),
        (r"/get_closest_persons_and_msgs", GiveClosestPersonsAndMsgs, dict(db=DB)),
        (r"/have_hebrew", HaveHebrew, dict(db=DB)),
        (r"/get_good_night_messages", GiveGoodNightMessages, dict(db=DB)),
        (r"/get_dreams_or_old_messages", GiveDreamsOrOldMessages, dict(db=DB)),
        (r"/get_most_active_groups_and_user_groups", GiveMostActiveGroupsAndUserGroups, dict(db=DB)),
        (r"/get_chat_archive", GiveChatArchive, dict(db=DB)),
    ], **settings)


if __name__ == "__main__":

    DB = WhatsAppDB()

    port = 8888
    app = make_app(DB)

    # enter webPage as the first argument to run the web page
    # TODO decide where to place in order to have good functionality- divide the server!
    if sys.argv[1] == 'WebPage':
        # A Chrome window to navigate to our site
        print("web Page")
        driver1 = Webdriver()
        driver1.browser.get("localhost:8888")  # TODO read about passing the DB to the handlers

    # save the data for future work
    elif sys.argv[1] == 'SaveData':
        print("scrapping and saving data to pickle")
        scrape_whatsapp(DB)

        DB.convert_to_datetime_and_sort()

        # DB.run_data_analysis_and_store_results()
        DB.save_db_to_files(".\\stored data\\")
        sys.exit()

    # load the last stored data and analyze it
    elif sys.argv[1] == 'LoadData':
        print('loading the data')
        DB.load_db_from_files(".\\stored data\\")

        DB.convert_to_datetime_and_sort()

        import DataAnalysisTestDriver
        DataAnalysisTestDriver.test_data_analysis(DB)
        DB.run_data_analysis_and_store_results()
        print("server keeps running for unity get requests")

    # just runs the scrapping and analysis
    else:
        print("scrape_whatsapp")
        scrape_whatsapp(DB)

        DB.convert_to_datetime_and_sort()
        import DataAnalysisTestDriver
        DataAnalysisTestDriver.test_data_analysis(DB)

        DB.run_data_analysis_and_store_results()
        print("server keeps running for unity get requests")

    app.listen(port)
    tornado.ioloop.IOLoop.current().start()




