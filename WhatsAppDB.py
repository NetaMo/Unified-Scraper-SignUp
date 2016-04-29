from pandas.tseries.frequencies import to_offset
from datetime import date, datetime
import pandas as pd


class WhatsAppDB:
    """
    stores and analyses all of the data scraped from the whats app web.
    """
    def __init__(self):
        print("initializing the DataFrames")

        self.contacts_df = pd.DataFrame(data=None, columns=["contactName", "contactType", "name", "text", "time"])  # TODO remove contactType
        self.contacts_df.contactType.astype('category', categories=["person", "group"])
        self.contacts_df.name.astype('category')
        
        self.groups_df = pd.DataFrame(columns=["groupName", "name", "messagesCount"]) # todo maybe make multi index

        self.user_name = ''

        # TODO add oldest_time

    def append_to_contacts_df(self, data_dict):
        """
        appends the dictionary data to the contacts data frame.
        :param data_dict: the dictionary to append
        """
        print("append_to_contacts_df")
        # data_json = self.request.body
        # content_type = self.request.headers.get('content-type', '')
        # content_type, params = parse_header(content_type)
        # if content_type.lower() != 'application/json':
        #     print("ERROR: not the right content")
        # charset = params.get('charset', 'UTF8')c
        # data = json.loads(data_json.decode(charset))
        print("data: " + str(data_dict))
        contact_name = data_dict["contact"]["name"]
        contact_type = data_dict["contact"]["type"] # TODO remove
        for message in data_dict["messages"][0]:
            name = message["name"]
            text = message["text"]

            self.contacts_df = self.contacts_df.append({'contactName': contact_name, 'contactType': contact_type, 'name': name, 'text': text,
                            'time': message["time"]}, ignore_index=True)
            #             todo check about chronological consistency
        print("the current state of contacts_df: ")
        print(self.contacts_df)
        print("===================================================")

    def convert_to_datetime_and_sort(self):
        """
        converts the time series to the datetime format and sorts the df descending by time
        """
        self.contacts_df.time = pd.to_datetime(self.contacts_df.time)
        self.contacts_df.sort_values('time', ascending=False, inplace=True)

    """""
    data analysis methods
    """""

    @staticmethod
    def is_language_hebrew(text):
        """
        checks a string if is has hebrew characters
        :param text: string to check
        :return: True if has hebrew
        """
        hebrew_letters = set("אבגדהוזחטיכלמנסעפצקרשת")
        if any((c in hebrew_letters) for c in text):
            return True
        else:
            return False

    def does_df_has_hebrew(self):  # todo maybe make check larger parts
        """
        checks if the contacts data frame text fields has hebrew chars
        :return: True if has hebrew
        """
        for text in list(self.contacts_df.head(10).text.values):
            if self.is_language_hebrew(text):
                return True

        for text in list(self.contacts_df.tail(10).text.values):
            if self.is_language_hebrew(text):
                return True
        return False

    @staticmethod
    def correct_time_for_whatsapp(x):
        """
        adjusts the time column for the way it is shown in WhatsApp
        :param x: the datetime field of the df
        :return: the corrected whatsapp time string
        """
        if x.date() == pd.to_datetime('today').date():
            return str(x.time())[:-3]  # exclude the seconds
        elif x.date() == (pd.to_datetime('today') - pd.DateOffset()).date():
            return 'Yesterday'
        else:
            return x.strftime('%m/%d/%y')

    def get_latest_chats(self, number_of_chats):
        """
        finds the latest 'number_of_chats' with name, text and time
        :param number_of_chats: how much chats to return
        :return: json with the latest 'number_of_chats' with name, text and time
        """
        latest_msgs_df = self.contacts_df.drop_duplicates(subset='contactName').head(number_of_chats)
        latest_msgs_df.time = latest_msgs_df.time.apply(self.correct_time_for_whatsapp)
        return latest_msgs_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def get_blast_from_the_past(self, past_fraction):
        """
        gets a contact that the user talked to a lot in the past
        :param past_fraction: the fraction part to go back in time
        :return: a row in the df of the person chosen
        """
        oldest_time = min(self.contacts_df.time)

        # noinspection PyTypeChecker
        past_chats_threshold_days = past_fraction * (pd.Timestamp(date(datetime.today().year, datetime.today().month,
                                                                       datetime.today().day)).date() - (oldest_time.date()))
        past_chats_threshold_date = oldest_time + to_offset(past_chats_threshold_days)
        df_past_chats = self.contacts_df.where(self.contacts_df.time <= past_chats_threshold_date).dropna()
        return df_past_chats.contactName.value_counts().head(1).index[0]

    def get_closest_persons_and_msg(self, number_of_persons, user_name, past_fraction_param):
        """
        finds the number_of_persons most talked persons and a message that has the user name in it.
        :param user_name: the name people call the user
        :param past_fraction_param: the fraction part to go back in time for the blast from the past
        :return: json with the data
        """
        closest_persons_ndarray = self.contacts_df.contactName.value_counts().head(number_of_persons).index
        i = 0
        closest_persons_df = pd.DataFrame()
        for contactName in closest_persons_ndarray:
            closest_persons_df = closest_persons_df.append({'contactName': contactName, 'text': user_name}, ignore_index=True)
            for index, col in self.contacts_df.iterrows():
                if col['contactName'] == contactName:
                    if user_name in col['text']:
                        closest_persons_df.iloc[i].text = col['text']
            i += 1

        blast = self.get_blast_from_the_past(past_fraction_param)
        closest_persons_df = closest_persons_df.append({"contactName": blast, "text": "im the blast fron the past"}, ignore_index=True)
        return closest_persons_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def get_good_night_messages(self):
        """
        finds messages containing good night words
        :return: json with the data
        """
        good_night_df = self.contacts_df[self.contacts_df.text.str.contains("good night|לילה טוב|Bonne nuit|bonne nuit|sweet dreams|ליל מנוחה")]
        good_night_df = good_night_df[['contactName', 'text']]
        return good_night_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')


    def get_dream_messages(self):  # todo check the results and decide on size
        """
        finds messages containing dream words
        :return: dataframe of the data above
        """
        good_night_df = self.contacts_df[self.contacts_df.text.str.contains(
            "חלמתי|חלומות|חלמת|dream|dreamt|dreaming|dreams|rêver|rêves|rêvé|rêve|reve|reves|rever|dreamed")]
        good_night_df = good_night_df[['contactName', 'text']]
        return good_night_df

    def get_old_messages(self, past_fraction):
        """
        finds old messages
        :param past_fraction: the fraction part to look at from the oldest msg
        :return: dataframe of the data above
        """
        # noinspection PyTypeChecker
        past_chats_threshold_days = past_fraction * (
            pd.Timestamp(date(datetime.today().year, datetime.today().month, datetime.today().day)).date() - (
                min(self.contacts_df.time).date()))
        past_chats_threshold_date = min(self.contacts_df.time) + to_offset(past_chats_threshold_days)
        print(past_chats_threshold_date)
        df_past_chats = self.contacts_df.where(self.contacts_df.time <= past_chats_threshold_date).dropna()
        return df_past_chats  # todo check how to filter good past msgs
    
    def get_dreams_or_old_messages(self, past_fraction_param):
        """
        decides what is better- old msgs or dream msgs and returns it
        :param past_fraction_param:
        :return: json with the data
        """
        dreams_df = self.get_dream_messages()

        num_of_sentences = 0
        for text in dreams_df.text:  # todo chceck the results of this logic
            if len(text.strip().split()) > 2:
                num_of_sentences += 1

        if num_of_sentences >= 5:
            return dreams_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')
        else:
            return self.get_old_messages(past_fraction_param).to_json(date_format='iso', double_precision=0,
                                                                                     date_unit='s', orient='records')

    def get_most_active_groups(self, max_number_of_groups):
        return list(self.groups_df['contactName'].value_counts().index)[:max_number_of_groups]  # TODO change to new api
    
    def get_users_activity_in_group(self, group_df):  # todo maybe make maximum number of users # TODO change to new api
        return list(group_df.name.value_counts().index)

    def get_most_active_groups_and_user_groups(self, max_number_of_groups):# TODO change to new api
        """
        finds the most active groups and sorts the users inside by their activity
        :param max_number_of_groups: how much groups to return
        :return: a dict with the data
        """
        most_active_groups_list = self.get_most_active_groups(max_number_of_groups)
        groups = self.groups_df.groupby('contactName')
        ret_dict_list = []
        i = 0
        for group_name in most_active_groups_list:
            for name, group in groups:
                if name is group_name:
                    ret_dict_list.append({})
                    ret_dict_list[i]["groupName"] = name
                    ret_dict_list[i]["groupContacts"] = self.get_users_activity_in_group(group)
            i += 1

        return ret_dict_list

    def get_chat_archive(self):
        """
        returns all of the chat history excluding groups
        :return: the data above in a data frame
        """
        # TODO add a feature for interesting part to start with
        return self.contacts_df.sort_values('contactName', ascending=True).text.values  # todo change the sort, maybe