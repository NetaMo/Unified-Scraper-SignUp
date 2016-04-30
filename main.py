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
        print("Stage 3: Name Submittted,Loading TermsPage")
        # These variables hold the users input
        first_name = self.get_argument("first")
        last_name = self.get_argument("last")

        # assign the first name to the user name attribute in DB
        self.db.user_name = first_name
        # TODO maybe ask for nickname for data analysis

        # writes the users name to file
        with open('users', 'a', encoding='utf8') as users_file:
            users_file.write(first_name + " " + last_name + "\n")


class TermAgreeHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        print("Stage 4: Agreed,Load whatssapp web")
        # run whats up web scrapper
        scrape_whatsapp(self.db)

        DB.convert_to_datetime_and_sort()
        import DataAnalysisTestDriver
        DataAnalysisTestDriver.test_data_analysis(DB)

"""""
make_app, settings, main
"""""

settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))


def make_app(db):
    print("make_app")
    return tornado.web.Application([(
        (r"/", LandingHandler)),
        (r"/agree", TermAgreeHandler, dict(db=DB)),
        (r"/namesubmit", NameSubmitHandler, dict(db=DB))
    ], **settings)


if __name__ == "__main__":

    DB = WhatsAppDB()

    port = 8888
    app = make_app(DB)

    # enter True as the first argument to run the web page
    # TODO decide where to place in order to have good functionality- divide the server!
    if sys.argv[1] == 'True':
        # A Chrome window to navigate to our site
        print("web Page")
        driver1 = Webdriver()
        driver1.browser.get("localhost:8888")  # TODO read about passing the DB to the handlers
    else:  # just runs the scrapping
        print("scrape_whatsapp")
        scrape_whatsapp(DB)

        DB.convert_to_datetime_and_sort()
        import DataAnalysisTestDriver
        DataAnalysisTestDriver.test_data_analysis(DB)

    app.listen(port)
    tornado.ioloop.IOLoop.current().start()



