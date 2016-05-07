import json
from datetime import date, datetime, time as dt
from itertools import groupby

import pandas as pd
from pandas.tseries.frequencies import to_offset
import numpy as np


class WhatsAppDB:
    """
    stores and analyses all of the data scraped from the whats app web.
    """
    def __init__(self):
        print("initializing the DataFrames")

        self.contacts_df = pd.DataFrame(data=None, columns=["contactName", "name", "text", "time"])
        self.contacts_df.name.astype('category')
        
        self.groups_df = pd.DataFrame(columns=["groupName", "name", "messagesCount", "totalMessages"])
        self.groups_df.messagesCount.astype(int)
        self.groups_df.totalMessages.astype(int)

        self.user_first_name = ""
        self.user_last_name = ""
        self.user_whatsapp_name = ""
        self.user_nicknames = []
        self.phone = ""

        # =====data analysis json outputs=====
        self.latest_chats = 0
        self.closest_persons_and_msg = 0
        self.have_hebrew = False  # boolean
        self.good_night_messages = 0
        self.dreams_or_old_messages = 0
        self.most_active_groups_and_user_groups = 0
        self.chat_archive = 0

    def set_user_whatsapp_name(self, user_whatsapp_name):
        self.user_whatsapp_name = user_whatsapp_name

    def append_to_groups_df(self, data_dict):
        """
        appends the dictionary data to the groups data frame.
        :param data_dict: the dictionary to append
        """
        print("append_to_groups_df")
        # print("data: " + str(data_dict))

        group_name = data_dict["contactName"]
        for name in iter(data_dict["contactMessageCounter"]):
            self.groups_df = self.groups_df.append({'groupName': group_name, 'name': name, 'messagesCount': data_dict[
                "contactMessageCounter"][name], 'totalMessages': data_dict['contactMessageTotal']}, ignore_index=True)

        # print("the current state of groups_df: ")
        # print(self.groups_df)
        # print("===================================================")

    def append_to_contacts_df(self, data_dict):
        """
        appends the dictionary data to the contacts data frame.
        :param data_dict: the dictionary to append
        """
        print("append_to_contacts_df")
        # print("data: " + str(data_dict))
        contact_name = data_dict["contact"]["name"]
        for message in data_dict["messages"][0]:
            name = message["name"]
            text = message["text"]

            self.contacts_df = self.contacts_df.append({'contactName': contact_name, 'name': name, 'text': text,
                                                        'time': message["time"]}, ignore_index=True)

        # print("the current state of contacts_df: ")
        # print(self.contacts_df)
        # print("===================================================")

    def convert_to_datetime(self):
        """
        converts the time series to the datetime format
        """
        self.contacts_df.time = pd.to_datetime(self.contacts_df.time)

    def sort(self):
        # sorts the df descending by time
        self.contacts_df.sort_values('time', ascending=False, inplace=True)

    def run_data_analysis_and_store_results(self):
        """
        runs all of the data analysis methods and store the resulted json outputs
        """
        self.chat_archive = self.get_chat_archive()

        self.latest_chats = self.get_latest_chats(6)

        number_of_contacts = 150
        past_fraction = 0.75
        self.closest_persons_and_msg = self.get_closest_persons_and_msg(number_of_contacts, past_fraction)

        self.have_hebrew = self.does_df_has_hebrew()

        self.good_night_messages = self.get_good_night_messages()

        past_fraction = 0.25
        self.dreams_or_old_messages = self.get_dreams_or_old_messages(past_fraction)

        max_num_of_groups = 5
        self.most_active_groups_and_user_groups = self.get_most_active_groups_and_user_groups(max_num_of_groups)

    def save_db_to_files(self, path):
        self.contacts_df.to_pickle(path + "saved_contacts_df")
        self.groups_df.to_pickle(path + "saved_groups_df")
        with open(path + "user name", 'w+', encoding='utf8') as file:
            file.write(self.user_name)

    def load_db_from_files(self, path):
        self.contacts_df = pd.read_pickle(path + "saved_contacts_df")
        self.groups_df = pd.read_pickle(path + "saved_groups_df")
        with open(path + "user name", 'r', encoding='utf8') as file:
            self.user_name = file.read()

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
        data = {"hebrew": False, "user_whatsapp_name":self.user_whatsapp_name, "user_os": "android"}
        for text in list(self.contacts_df.head(10).text.values):
            if self.is_language_hebrew(text):
                data["hebrew"] = True

        for text in list(self.contacts_df.tail(10).text.values):
            if self.is_language_hebrew(text):
                data["hebrew"] = True

        return json.dumps(data)

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
        sliced_df = latest_msgs_df[['contactName', 'text', 'time']]
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

    def get_closest_persons_and_msg(self, number_of_persons, past_fraction_param):
        """
        finds the number_of_persons most talked persons and a message that has the user name in it.
        :param number_of_persons: the number of close persons to find.
        :param past_fraction_param: the fraction part to go back in time for the blast from the past
        :return: json with the data
        """
        closest_persons_ndarray = self.contacts_df.contactName.value_counts().head(number_of_persons).index


        self.user_nicknames.append(self.user_first_name)
        i = 0
        closest_persons_df = pd.DataFrame()
        for contactName in closest_persons_ndarray:
            closest_persons_df = closest_persons_df.append({'contactName': contactName, 'text': self.user_first_name}, ignore_index=True)
            for index, col in self.contacts_df.iterrows():
                if col['contactName'] == contactName:
                    if any(word in col['text'] for word in self.user_nicknames):
                        closest_persons_df.iloc[i].text = col['text']
            i += 1

        blast = self.get_blast_from_the_past(past_fraction_param)
        closest_persons_df = closest_persons_df.append({"contactName": blast, "text": "im the blast from the past"},
                                                       ignore_index=True)
        return closest_persons_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def get_good_night_messages(self):
        """
        finds messages containing good night words
        :return: json with the data
        """
        good_night_df = self.contacts_df[self.contacts_df.text.str.lower().str.contains("good night|לילה טוב|bonne nuit|sweet dreams|ליל "
                                                                             "מנוחה")]

        good_night_df = good_night_df[['contactName', 'text']]
        return good_night_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def get_dream_messages(self):  # todo check the results and decide on size
        """
        finds messages containing dream words
        :return: dataframe of the data above
        """
        good_night_df = self.contacts_df[self.contacts_df.text.str.lower().str.contains(
            "חלמתי|חלומות|חלמת|dream|dreamt|dreaming|dreams|rêver|rêves|rêvé|rêve|reve|reves|rever|dreamed")]
        good_night_df = good_night_df[['contactName', 'text']]
        return good_night_df[['contactName', 'text']]

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
        # print(past_chats_threshold_date)
        df_past_chats = self.contacts_df.where(self.contacts_df.time <= past_chats_threshold_date).dropna()
        return df_past_chats[['contactName', 'text']]  # todo check how to filter good past msgs
    
    def get_dreams_or_old_messages(self, past_fraction_param):
        """
        decides what is better- old msgs or dream msgs and returns it
        :param past_fraction_param:
        :return: json with the data
        """
        dreams_df = self.get_dream_messages()

        num_of_sentences = 0
        for text in dreams_df.text:  # todo check the results of this logic
            if len(text.strip().split()) > 2:
                num_of_sentences += 1

        if num_of_sentences >= 5:
            return dreams_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')
        else:
            return self.get_old_messages(past_fraction_param).to_json(date_format='iso', double_precision=0,
                                                                                     date_unit='s', orient='records')


    def get_most_active_groups_and_user_groups(self, max_number_of_groups):
        """
        finds the most active groups and gets the users inside by their activity
        :param max_number_of_groups: how much groups to return
        :return: a json with the data
        """

        # TODO if we load same number of messages for each group- then we need to change the sort of the active groups
        # TODO so we can sort the intensity of the groups by the earliest date found in each group.
        self.groups_df.sort_values(['totalMessages', 'groupName', 'messagesCount'], ascending=False, inplace=True)
        group_names = self.groups_df.groupName.unique()[:max_number_of_groups]

        result_df = self.groups_df.loc[self.groups_df['groupName'].isin(group_names)]
        sliced_df = result_df[['groupName', 'name']]

        # print(sliced_df) TODO check its correct!

        # sliced_df = sliced_df.append({'WhatsAppUserName': self.user_whatsapp_name}, ignore_index=True)
        # res_dict = sliced_df.to_dict(orient='records')
        # res_dict["WhatsAppUserName"] = self.user_whatsapp_name

        json = sliced_df.to_json(date_format='iso', double_precision=0, date_unit='s', )
        return self._clean_hidden_chars(json)
        # return json.dumps(res_dict)

    def _clean_hidden_chars(self, s):
        hiddens = ['\\xa0']  # In case we find more of them, use \\ and not \
        for hidden in hiddens:
            s = s.replace(hidden, '')
        return s

    def amount_of_letter_sequences(self, str):
        ''' Helper Function. returns the amount of letter sequences longer than min_amount '''

        LETTER_SEQ_MIN_LEN = 6

        letters_legend = [[letter, len(list(amount))] for letter, amount in groupby(str)]
        amount_of_seq = [c[1]>=LETTER_SEQ_MIN_LEN for c in letters_legend].count(True)
        return amount_of_seq

    def get_chat_archive(self):
        """
        Mostly written by Daniel the neighbor, ask him for the logic
        """

        START_INTERESTING_TIME = dt(00, 1, 0)
        END_INTERESTING_TIME = dt(4, 00, 0)
        ENVIRONMENT_SIZE = 3    # one-sided (i.e. environment is actually twice bigger)
        INTERESTING_ROWS_EXTRA_BEFORE = 20
        INTERESTING_ROWS_EXTRA_AFTER = 20

        df = self.contacts_df

        # (+) add column: message length
        df['mes_len'] = df.text.apply(len)

        # (+) add column: is time of message between START_INTERESTING_TIME and END_INTERESTING_TIME (True if yes)
        # returns boolean mask (is brackets) of True where 'time' is within boundaries
        df['is_night'] = df.isin(
            df.set_index(keys='time').between_time(START_INTERESTING_TIME, END_INTERESTING_TIME).index.tolist()
        ).time

        # (+) add column: does contain long letter sequence (longer than LETTER_SEQ_LEN)
        df['amount_of_letter_seq'] = df.text.apply(self.amount_of_letter_sequences)

        # >>> compute grade; how interesting is the message by itself (w.o. context)?    higher is better. <<<
        # you can use adjust weights
        df['self_interest_grade'] = 1 * df.mes_len \
                                    + 400 * df.is_night \
                                    - 5 * df.amount_of_letter_seq

        # (+) add column: is message part of sequence of interesting messages (relying on self_interest_grade)
        #   notice that it doesn't calculate for the first and last ENVIRONMENT_SIZE rows (you wouldn't use them anyway)
        l = df.self_interest_grade.tolist()
        df['interest_grade'] = [np.sum(l[i[0]-ENVIRONMENT_SIZE:i[0]+ENVIRONMENT_SIZE]) for i in enumerate(l)]

        # Get the ID of the interesting message
        interesting_message_row_id = int(df.interest_grade.idxmax())

        # Remove the columns that were used for calculations
        del df['mes_len']
        del df['is_night']
        del df['amount_of_letter_seq']
        del df['self_interest_grade']
        del df['interest_grade']

        # Get name of interesting contact, his messages and the ID of the last message from him
        interesting_message = df.iloc[interesting_message_row_id]
        print('The interesting message is: {}'.format(interesting_message))
        contact_name_interesting_message = interesting_message['contactName']
        messages_of_contact = df[df.contactName.str.contains(contact_name_interesting_message)]
        index_last_message_from_contact = len(messages_of_contact) - 1

        # Indexes of messages before and after the interesting message
        index_interesting_row_before = interesting_message_row_id - INTERESTING_ROWS_EXTRA_BEFORE
        index_interesting_row_after = interesting_message_row_id + INTERESTING_ROWS_EXTRA_AFTER

        # Check if the index before isn't before 0
        if index_interesting_row_before < 0:
            diff = abs(index_interesting_row_before)

            # Check if the index after isn't above the last message index
            if index_interesting_row_after + diff < index_last_message_from_contact:
                index_interesting_row_after += diff
            index_interesting_row_before = 0

        # Check if index after isn't over the last message index
        if index_interesting_row_after > index_last_message_from_contact:
            diff = index_interesting_row_after - index_last_message_from_contact

            # Check if the index before isn't below zero if we remove the diff from it
            if index_interesting_row_before - diff >= 0:
                index_interesting_row_before -= diff
            index_interesting_row_after = index_last_message_from_contact - 1

        # Slice the interesting message, before and after
        interesting_messages = df.iloc[index_interesting_row_before:index_interesting_row_after]
        print("The interesting messages are: \n{}".format(interesting_messages))

        # Get the length of the DataFrame
        df_len = len(df)
        half_len = int(df_len/2)
        # The first and second half of it
        first_half_df = df.iloc[0:half_len]
        second_half = df.iloc[half_len:df_len - 1]

        # Append the first half, interesting messages and then second half
        df_with_interesting_messages_in_middle = first_half_df.append(interesting_messages, ignore_index=True).append(second_half, ignore_index=True)

        # Sort the DataFrame, for usage in future methods
        self.sort()

        return df_with_interesting_messages_in_middle.to_json(date_format='iso', double_precision=0, date_unit='s', )
