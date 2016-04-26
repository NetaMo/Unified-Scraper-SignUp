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

def isTyping():

    driver = Webdriver()  # create new driver
    scraper = WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    scraper.scrape()  # scrape
    driver.close()  # close driver

settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))

class LandingHandler(tornado.web.RequestHandler):
    def get(self):
        print("Stage 1: Loading HomePage")
        self.render("LandingPage.html")

class NameSubmitHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 3: Name Submittted,Loading TermsPage")
        # These variables hold the users input
        firstName = self.get_argument("first")
        lastName = self.get_argument("last")
        print(firstName)
        print(lastName)
        # now we can send a string to the front end with the following syntax:
        # self.write("string message")
        # self.finish()
        # This loads the terms page

class TermAgreeHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 4: Agreed,Load whatssapp web")
        # Insert whats up web run here
        isTyping()

def make_app():
    print("make_app")
    return tornado.web.Application([
        (r"/", LandingHandler),
        (r"/agree", TermAgreeHandler),
        (r"/namesubmit", NameSubmitHandler),
    ], **settings)


if __name__ == "__main__":
    port = 8888
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

def isTyping():

    driver = Webdriver()  # create new driver
    # driver.SwitchTo().Window("//name of the window");

    scraper = WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    scraper.scrape()  # scrape

    driver.close()  # close driver

# isTyping()