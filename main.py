from Webdriver import Webdriver
from WhatsAppWebScraper import WhatsAppWebScraper
import tornado.ioloop
import tornado.web
import json
import os
from cgi import parse_header
import pandas as pd

"""
Main isTyping application.
"""
# A Chrome window to navigate to our site
driver1 = Webdriver()
driver1.browser.get("localhost:8888")

def isTyping():

    driver = Webdriver()  # create new driver
    # window_before = driver.browser.window_handles[0]
    window_after = driver.getBrowser().window_handles[0]
    driver.getBrowser().switch_to.window(window_after)
    scraper = WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    print("after scrape")
    scraper.scrape()  # scrape
    print("after scrape")
    driver.close()  # close driver


settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))

class LandingHandler(tornado.web.RequestHandler):
    def get(self):
        print("Stage 1: Loading HomePage")
        self.render("LandingPage.html")

class NameSubmitHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 3: Name Submittted, Loading TermsPage")
        # These variables hold the users input
        firstName = self.get_argument("first")
        lastName = self.get_argument("last")
        print("User first name:", firstName)
        print("User last name:", lastName)

class NickNameSubmitHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 2: Nick Name Submittted, Loading Full Name")
        # These variables hold the users input
        nickName = self.get_argument("nick")
        print("User NickName:", nickName)


class TermAgreeHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 4: Agreed, Go to phone sort")

class PhoneSortHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 5: Load Phone Sort")


class LetsGoHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 7: Lets Fucking GO!, Load whatssapp web!")
        # Insert whats up web run here
        isTyping()

class IphoneHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 6: Iphone Chosen")


class AndroidHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 4: Agreed, Load whatssapp web")
        # Insert whats up web run here
        # isTyping()

def make_app():
    print("make_app")
    return tornado.web.Application([
        (r"/", LandingHandler),
        (r"/agree", TermAgreeHandler),
        (r"/namesubmit", NameSubmitHandler),
        (r"/nicknamesubmit", NickNameSubmitHandler),
        (r"/phonesort", PhoneSortHandler),
        (r"/iphone", IphoneHandler),
        (r"/android", AndroidHandler),
        (r"/letsgo", LetsGoHandler),
    ], **settings)


if __name__ == "__main__":
    port = 8888
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()




