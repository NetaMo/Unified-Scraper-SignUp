import sys
import os
from Webdriver import Webdriver
import WhatsAppWebScraper
import tornado.ioloop
import tornado.web
from WhatsAppDB import WhatsAppDB

"""
run the WhatsApp web scrapper.
"""


def scrape_whatsapp(db):
    driver = Webdriver()  # create new driver
    # window_before = driver.browser.window_handles[0]
    window_after = driver.getBrowser().window_handles[0]
    driver.getBrowser().switch_to.window(window_after)
    scraper = WhatsAppWebScraper.WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    print("before scrape")
    db = scraper.scrape(db)  # scrape
    print("after scrape")
    driver.close()  # close driver

    return db


"""""
web page handlers:
"""""


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

        # TODO assign the first name to the user name attribute in DB
        # TODO maybe ask for nickname for data analysis

        # now we can send a string to the front end with the following syntax:
        # self.write("string message")
        # self.finish()
        # This loads the terms page


class TermAgreeHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 4: Agreed,Load whatssapp web")
        # Insert whats up web run here
        # scrape_whatsapp() # TODO figure out how to send the DB here


"""""
make_app, settings, main
"""""

settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))


def make_app():
    print("make_app")
    return tornado.web.Application([
        (r"/", LandingHandler),
        (r"/agree", TermAgreeHandler),
        (r"/namesubmit", NameSubmitHandler),
        # (r"/chat", WhatsAppHandler),
        # (r"/chatFinished", FinishedWhatsAppHandler)
    ], **settings)


if __name__ == "__main__":

    DB = WhatsAppDB()

    port = 8888
    app = make_app()

    # enter True as the first argument to run the web page
    # TODO decide where to place in order to have good functionality- divide the server!
    if sys.argv[1] == 'True':
        # A Chrome window to navigate to our site
        print("web Page")
        driver1 = Webdriver()
        driver1.browser.get("localhost:8888")  # TODO read about passing the DB to the handlers
    else:  # just runs the scrapping
        print("scrape_whatsapp")
        DB = scrape_whatsapp(DB)

        DB.convert_to_datetime_and_sort()
        import DataAnalysisTestDriver
        DataAnalysisTestDriver.test_data_analysis(DB)

    app.listen(port)
    tornado.ioloop.IOLoop.current().start()




