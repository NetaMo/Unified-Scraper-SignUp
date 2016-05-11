from selenium import webdriver
from selenium.webdriver.chrome.options import Options

"""
This class opens and controls a web browser (for example a Chrome browser).
"""
class Webdriver:

    def __init__(self):
        chromeOptions = Options()
        chromeOptions.add_argument("--kiosk")  # fullscreen mode
        # self.browser = webdriver.Chrome()  # Create Chrome browser
        # self.browser = webdriver.Chrome(executable_path="/Users/GN3/Desktop/chromedriver",chrome_options=chromeOptions)  # Create Chrome browser
        self.browser = webdriver.Chrome(executable_path="C:\\Users\\maoze\\AppData\\Local\\Programs\\Python\\Python35-32\\Scripts\\chromedriver.exe", chrome_options=chromeOptions)  # Create Chrome browser
        # self.browser = webdriver.Chrome(executable_path="/Users/GN3/Desktop/chromedriver")  # Create Chrome browser
        # self.browser = webdriver.Chrome(executable_path="C:\\Users\\maoze\\AppData\\Local\\Programs\\Python\\Python35-32\\Scripts\\chromedriver.exe,,chrome_options=chromeOptions")  # Create Chrome browser
        # self.browser = webdriver.Chrome(executable_path="C:\Program Files\Python35\Scripts\chromedriver.exe,,chrome_options=chromeOptions")  # Create Chrome browser


        self.browser.maximize_window()

    def close(self):
        """
        Close browser
        """
        self.browser.close()

    def getBrowser(self):
        return self.browser