from selenium import webdriver

"""
This class opens and controls a web browser (for example a Chrome browser).
"""
class Webdriver:

    def __init__(self):
        # self.browser = webdriver.Chrome()  # Create Chrome browser
        # self.browser = webdriver.Chrome(executable_path="/Users/GN3/Desktop/chromedriver")  # Create Chrome browser
        self.browser = webdriver.Chrome("env/chromedriver")  # Create Chrome browser
        self.browser.maximize_window()

    def close(self):
        """
        Close browser
        """
        self.browser.close()

    def getBrowser(self):
        return self.browser