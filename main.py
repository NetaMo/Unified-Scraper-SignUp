import os
from Webdriver import Webdriver
from WhatsAppWebScraper import WhatsAppWebScraper
import tornado.ioloop
import tornado.web
import json
from cgi import parse_header
import pandas as pd
from pandas.tseries.frequencies import to_offset
from datetime import date, datetime

"""
Main "is typing" application.
"""
# A Chrome window to navigate to our site TODO decide where to place in order to have good functionality
driver1 = Webdriver()
driver1.browser.get("localhost:8888")


def is_typing():
    driver = Webdriver()  # create new driver
    # window_before = driver.browser.window_handles[0]
    window_after = driver.getBrowser().window_handles[0]
    driver.getBrowser().switch_to.window(window_after)
    scraper = WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    print("before scrape")
    scraper.scrape()  # scrape
    print("after scrape")
    driver.close()  # close driver


"""""
whatsApp scraping handlers
"""""
class WhatsAppHandler(tornado.web.RequestHandler):
    def post(self):
        global df
        print("GetWhatsAppChat post handler")
        data_json = self.request.body
        content_type = self.request.headers.get('content-type', '')
        content_type, params = parse_header(content_type)
        if content_type.lower() != 'application/json':
            print("ERROR: not the right content")
        charset = params.get('charset', 'UTF8')
        data = json.loads(data_json.decode(charset))
        print("data: " + str(data))
        contact_name = data["contact"]["name"]
        contact_type = data["contact"]["type"]
        for message in data["messages"][0]:
            name = message["name"]
            text = message["text"]

            df = df.append({'contactName': contact_name, 'contactType': contact_type, 'name': name, 'text': text,
                            'time': message["time"]}, ignore_index=True)
#             todo check about chronological consistency
        print("the current df: ")
        print(df)
        print("===================================================")


class FinishedWhatsAppHandler(tornado.web.RequestHandler):

    def post(self):
        print("FinishedWhatsAppHandler")
        global df
        global df_no_groups
        global df_groups
        global user_name

        df.time = pd.to_datetime(df.time)
        df.sort_values('time', ascending=True)

        df_groups = df[df.contactType == 'group']
        df_no_groups = df[df.contactType == 'person']

        print("=============================================")
        print("df:")
        print(df)
        print("=============================================")

        print("me:")
        print(df[df["name"] == 'Me'])
        print("=============================================")


        print("get_last_chats")
        print(json.loads(DataAnalysisMethods.get_last_chats(6)))
        print("----------------------------------")

        print("get_closest_persons_and_msg")
        number_of_contacts = 150
        past_fraction = 0.75
        print(json.loads(DataAnalysisMethods.get_closest_persons_and_msg(number_of_contacts, user_name, past_fraction)))
        print("----------------------------------")

        print("does_df_has_hebrew")
        print(DataAnalysisMethods.does_df_has_hebrew())
        print("----------------------------------")

        print("get_good_night_messages")
        print(json.loads(DataAnalysisMethods.get_good_night_messages()))
        print("----------------------------------")

        print("get_dreams_or_old_messages")
        past_fraction = 0.25
        print(json.loads(DataAnalysisMethods.get_dreams_or_old_messages(past_fraction)))
        print("----------------------------------")

        print("get_most_active_groups_and_user_groups")
        max_num_of_groups = 5
        print(DataAnalysisMethods.get_most_active_groups_and_user_groups(max_num_of_groups))
        print("----------------------------------")

        print("get_chat_archive")
        print(DataAnalysisMethods.get_chat_archive())
        print("----------------------------------")


"""""
data analysis methods
"""""
class DataAnalysisMethods:
    global df_no_groups
    global df_groups
    global df

    @staticmethod
    def is_language_hebrew(text):
        hebrew_letters = set("אבגדהוזחטיכלמנסעפצקרשת")
        if any((c in hebrew_letters) for c in text):
            return True
        else:
            return False

    @staticmethod
    def does_df_has_hebrew():  # todo maybe make check larger
        for text in list(df.head(10).text.values):
            if DataAnalysisMethods.is_language_hebrew(text):
                return True

        for text in list(df.tail(10).text.values):
            if DataAnalysisMethods.is_language_hebrew(text):
                return True
        return False

    @staticmethod
    def correct_time_for_whatsapp(x):
        if x.date() == pd.to_datetime('today').date():
            return str(x.time())[:-3]  # exclude the seconds
        elif x.date() == (pd.to_datetime('today') - pd.DateOffset()).date():
            return 'Yesterday'
        else:
            return x.strftime('%m/%d/%y')

    ## returns the last number_of_chats with name, text and time
    @staticmethod
    def get_last_chats(number_of_chats):
        latest_msgs_df = df.drop_duplicates(subset='contactName').head(number_of_chats)
        latest_msgs_df.time = latest_msgs_df.time.apply(DataAnalysisMethods.correct_time_for_whatsapp)
        return latest_msgs_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')
        # todo if group edit the message with the sender

    ## gets a contact that the user talked to a lot in the past
    @staticmethod
    def get_blast_from_the_past(past_fraction):
        past_chats_threshold_days = past_fraction * (
            pd.Timestamp(date(datetime.today().year, datetime.today().month, datetime.today().day)).date() - (
                         min(df_no_groups.time).date()))
        past_chats_threshold_date = min(df_no_groups.time) + to_offset(past_chats_threshold_days)
        print(past_chats_threshold_date)
        df_past_chats = df_no_groups.where(df_no_groups.time <= past_chats_threshold_date).dropna()
        return df_past_chats.contactName.value_counts().head(1).index[0]

    ## finds the number_of_persons most talked persons and a message that has the user name in it.
    @staticmethod
    def get_closest_persons_and_msg(number_of_persons, user_name, past_fraction_param):
        closest_persons_ndarray = df_no_groups.contactName.value_counts().head(number_of_persons).index
        i = 0
        closest_persons_df = pd.DataFrame()
        for contactName in closest_persons_ndarray:
            closest_persons_df = closest_persons_df.append({'contactName': contactName, 'text': user_name}, ignore_index=True)
            for index, col in df_no_groups.iterrows():
                if col['contactName'] == contactName:
                    if user_name in col['text']:
                        closest_persons_df.iloc[i].text = col['text']
            i += 1

        blast = DataAnalysisMethods.get_blast_from_the_past(past_fraction_param)
        closest_persons_df = closest_persons_df.append({"contactName": blast, "text": "im the blast fron the past"}, ignore_index=True)
        return closest_persons_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    @staticmethod
    def get_good_night_messages():
        good_night_df = df_no_groups[df_no_groups.text.str.contains("good night|לילה טוב|Bonne nuit|bonne nuit|sweet dreams|ליל מנוחה")]
        good_night_df = good_night_df[['contactName', 'text']]
        return good_night_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    @staticmethod
    def get_dream_messages():  # todo check the results and decide on size
        good_night_df = df_no_groups[df_no_groups.text.str.contains(
            "חלמתי|חלומות|חלמת|dream|dreamt|dreaming|dreams|rêver|rêves|rêvé|rêve|reve|reves|rever|dreamed")]
        good_night_df = good_night_df[['contactName', 'text']]
        return good_night_df

    @staticmethod
    def get_old_messages(past_fraction):
        past_chats_threshold_days = past_fraction * (
            pd.Timestamp(date(datetime.today().year, datetime.today().month, datetime.today().day)).date() - (
                min(df_no_groups.time).date()))
        past_chats_threshold_date = min(df_no_groups.time) + to_offset(past_chats_threshold_days)
        print(past_chats_threshold_date)
        df_past_chats = df_no_groups.where(df_no_groups.time <= past_chats_threshold_date).dropna()
        return df_past_chats  # todo check how to filter good past msgs


    @staticmethod
    def get_dreams_or_old_messages(past_fraction_param):
        dreams_df = DataAnalysisMethods.get_dream_messages()

        num_of_sentences = 0
        for text in dreams_df.text:  # todo chceck the results of this logic
            if len(text.strip().split()) > 2:
                num_of_sentences += 1

        if num_of_sentences >= 5:
            return dreams_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')
        else:
            return DataAnalysisMethods.get_old_messages(past_fraction_param).to_json(date_format='iso', double_precision=0,
                                                                                     date_unit='s', orient='records')

    @staticmethod
    def get_most_active_groups(max_number_of_groups):
        return list(df_groups['contactName'].value_counts().index)[:max_number_of_groups]

    @staticmethod
    def get_users_activity_in_group(group_df):  # todo maybe make maximum number of users
        return list(group_df.name.value_counts().index)

    @staticmethod
    def get_most_active_groups_and_user_groups(max_number_of_groups):
        most_active_groups_list = DataAnalysisMethods.get_most_active_groups(max_number_of_groups)
        groups = df_groups.groupby('contactName')
        ret_dict_list = []
        i = 0
        for group_name in most_active_groups_list:
            for name, group in groups:
                if name is group_name:
                    ret_dict_list.append({})
                    ret_dict_list[i]["groupName"] = name
                    ret_dict_list[i]["groupContacts"] = DataAnalysisMethods.get_users_activity_in_group(group)
            i += 1

        return ret_dict_list

    @staticmethod
    def get_chat_archive():
        return df.sort_values('contactName', ascending=True).text.values  # todo change the sort, maybe



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

        global user_name
        user_name = firstName  # TODO maybe ask for nickname for data analysis
        # now we can send a string to the front end with the following syntax:
        # self.write("string message")
        # self.finish()
        # This loads the terms page

class TermAgreeHandler(tornado.web.RequestHandler):

    def get(self):
        print("Stage 4: Agreed,Load whatssapp web")
        # Insert whats up web run here
        is_typing()


"""""
make_app, seetings, main, and init_df
"""""


def init_df():
    print("initializing the DB")
    empty_df = pd.DataFrame(data=None, columns=["contactName", "contactType", "name", "text", "time"])
    empty_df.contactType.astype('category', categories=["person", "group"])
    empty_df.name.astype('category')
    return empty_df

settings = dict(
    static_path=os.path.join(os.path.dirname(__file__), "static")
)

def make_app():
    print("make_app")
    return tornado.web.Application([
        (r"/", LandingHandler),
        (r"/agree", TermAgreeHandler),
        (r"/namesubmit", NameSubmitHandler),
        (r"/chat", WhatsAppHandler),
        (r"/chatFinished", FinishedWhatsAppHandler)], **settings)


if __name__ == "__main__":
    df = init_df()
    df_no_groups = pd.DataFrame()
    df_groups = pd.DataFrame()
    user_name = ""
    port = 8888
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

