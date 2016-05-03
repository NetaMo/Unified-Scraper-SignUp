from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

"""
This class opens and controls a web browser (for example a Chrome browser).
"""
class Webdriver:

    def __init__(self):
        # self.browser = webdriver.Chrome(executable_path="/Users/GN3/Desktop/chromedriver")  # Create Chrome browser
        self.browser = webdriver.Chrome(executable_path="C:\Python34\Scripts\chromedriver.exe")  # Create Chrome browser
        self.browser.maximize_window()

    def close(self):
        """
        Close browser
        """
        self.browser.close()

    def getBrowser(self):
        return self.browser