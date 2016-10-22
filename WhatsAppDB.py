import json
from datetime import time as dt
from itertools import groupby
from datetime import datetime, date, timedelta

import numpy as np
import pandas as pd

import WhatsAppWebScraper

# suppress warnings
pd.options.mode.chained_assignment = None  # default='warn'
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class WhatsAppDB:
    """
    stores and analyses all of the data scraped from the whats app web.
    """
    def __init__(self):
        print("initializing the DataFrames")

        # self.contacts_df = pd.DataFrame(data=None, columns=["contactName", "name", "text", "time"])
        # self.contacts_df.name.astype('category')

        # self.groups_df = pd.DataFrame(columns=["groupName", "name", "messagesCount", "totalMessages"])
        # self.groups_df.messagesCount.astype(int)
        # self.groups_df.totalMessages.astype(int)

        self.user_first_name = ""
        self.user_last_name = ""
        self.user_whatsapp_name = ""
        self.user_nickname = ""
        self.phone = ""
        self.user_language = "heb"      # todo take from site

        # self.latest_contacts = []

        # =====data analysis json outputs=====
        self.latest_chats = 0
        self.my_name_messages = 0
        self.amphi_data = 0
        self.good_night_messages = 0
        self.dreams_or_old_messages = 0
        self.most_interesting = 0
        # self.love_messages = 0        not in v.liege

        # self.closest_persons_and_msg = 0
        # self.have_hebrew = False  # boolean
        # self.most_active_groups_and_user_groups = 0
        # self.chat_archive = 0

    def add_latest_contacts(self, name):
        self.latest_contacts.append(name)

    def get_first_name(self):
        return self.user_first_name

    def get_nickname(self):
        return self.user_nickname

    def set_amphi_data(self, arr_dict):
        self.amphi_data = arr_dict

    def set_user_whatsapp_name(self, user_whatsapp_name):
        self.user_whatsapp_name = user_whatsapp_name

    def append_to_groups_df(self, data_dict):
        """
        appends the dictionary data to the groups data frame.
        :param data_dict: the dictionary to append
        """
        # print("append_to_groups_df")
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
        # print("append_to_contacts_df")
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
        # How many contacts to show in coloseum
        number_of_contacts = 60

        # the maximum number of groups to output in the get_most_active_groups_and_user_groups function
        max_num_of_groups = 5

        max_group_size = 5

        self.convert_to_datetime()

        self.chat_archive = self.get_chat_archive()

        self.latest_chats = self.get_latest_chats(WhatsAppWebScraper.WhatsAppWebScraper.NUMBER_OF_PERSON_CONTACT_PICTURES)

        self.closest_persons_and_msg = self.get_closest_persons_and_msg(number_of_contacts)

        self.have_hebrew = self.does_df_has_hebrew()

        self.good_night_messages = self.get_good_night_messages()

        self.dreams_or_old_messages = self.get_dreams_or_old_messages()

        self.most_active_groups_and_user_groups = self.get_most_active_groups_and_user_groups(max_num_of_groups, max_group_size)

    def save_db_to_files(self, path):
        self.contacts_df.to_pickle(path + "saved_contacts_df")
        self.groups_df.to_pickle(path + "saved_groups_df")
        # with open(path + "user name", 'w+', encoding='utf8') as file:
        #     file.writelines(self.user_first_name, self.user_last_name, self.user_whatsapp_name, self.user_nicknames, self.phone)


    def load_db_from_files(self, path):
        self.contacts_df = pd.read_pickle(path + "saved_contacts_df")
        self.groups_df = pd.read_pickle(path + "saved_groups_df")
        # with open(path + "user name", 'r', encoding='utf8') as file:
        #     self.user_name = file.read()

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

    def does_df_has_hebrew(self):
        """
        checks if the contacts data frame text fields has hebrew chars
        :return: True if has hebrew
        """
        data = {"hebrew": False, "user_whatsapp_name":self.user_whatsapp_name, "user_os":self.phone}
        for text in list(self.contacts_df.head(20).text.values):
            if self.is_language_hebrew(text):
                data["hebrew"] = True

        for text in list(self.contacts_df.tail(20).text.values):
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
            return str(x.time())  # exclude the seconds
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
        # latest_msgs_df = self.contacts_df.drop_duplicates(subset='contactName').head(number_of_chats)

        latest_msgs_df = self.contacts_df.drop_duplicates(subset='contactName')

        res_df = pd.DataFrame()

        for contact_name in self.latest_contacts:
            res_df = res_df.append(latest_msgs_df[latest_msgs_df["contactName"] == contact_name], ignore_index=True)

        # res_df = latest_msgs_df.loc[latest_msgs_df['contactName'].isin(self.latest_contacts)]

        res_df.time = latest_msgs_df.time.apply(self.correct_time_for_whatsapp)
        sliced_df = res_df[['contactName', 'text', 'time']]
        return sliced_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def get_blast_from_the_past(self):
        """
        Return name of the last person you talked to.
        :return: string
        """

        # Last night fix - returns last contact name in dictionary
        return self.contacts_df.tail(1).values[0][0]

        # oldest_time = min(self.contacts_df.time)
        #
        # # noinspection PyTypeChecker
        # past_chats_threshold_days = past_fraction * (pd.Timestamp(date(datetime.today().year, datetime.today().month,
        #                                                                datetime.today().day)).date() - (oldest_time.date()))
        # past_chats_threshold_date = oldest_time + to_offset(past_chats_threshold_days)
        # df_past_chats = self.contacts_df.where(self.contacts_df.time <= past_chats_threshold_date).dropna()
        # return df_past_chats.contactName.value_counts().head(1).index[0]

    def get_closest_persons_and_msg(self, number_of_persons):
    # def get_closest_persons_and_msg(number_of_persons=40):

        df = self.contacts_df[self.contacts_df['contactName'] == self.contacts_df['name']]
        # df = pd.read_pickle('saved_contacts_df')
        # df['time'] = pd.to_datetime(df['time'])
    
        # (+) add column: message length
        df = df[['contactName', 'text']]
        df['count_val'] = df.groupby(['contactName']).transform('count')
        df['mes_len'] = df.text.apply(len)
    
        df.sort_values(['count_val', 'contactName'], inplace=True, ascending=False)
    
        return_df = df.drop_duplicates("contactName", keep='first')
    
        for contact in df.contactName.unique().tolist():
            # matched = [s for s in sorted(df[df.contactName == contact].text.tolist()) if ("p" or "r") in s]
            matched = [s for s in sorted(df[df.contactName == contact].text.tolist()) if
                       (self.user_first_name or self.user_last_name or self.user_nickname) in s]
            if matched:
                return_df.text[return_df.contactName == contact] = matched[-0]
            else:
                # return_df.text[return_df.contactName == contact] = "boring"
                return_df.text[return_df.contactName == contact] = self.user_first_name
    
        # return_df = return_df[:40]
        return_df = return_df[:number_of_persons]
    
        blast = self.get_blast_from_the_past()
        return_df = return_df.append({"contactName": blast, "text": "im the blast from the past"}, ignore_index=True)
    
        return return_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def get_good_night_messages(self):
        """
        finds messages containing good night word
        :return: json with the data
        """
        good_night_df = self.contacts_df[self.contacts_df.text.str.lower().str.contains(
        "good night|לילה טוב|bonne nuit|sweet dreams|ער\?|ערה\?|ער במקרה\?|ערה במקרה\?")]
        
        dreams_df = self.contacts_df[self.contacts_df.text.str.lower().str.contains(
            "חלמתי|חלומות|חלמת|dream|dreamt|dreaming|dreams|dreamed|חלום|חולם")]

        good_night_df['word_amount'] = good_night_df.text.apply(self.get_word_count)
        good_night_df = good_night_df[good_night_df.word_amount < 15]
        good_night_df = good_night_df[['contactName', 'text']]
        good_night_df['count_val'] = good_night_df.groupby(['contactName']).transform('count')
        good_night_df = good_night_df.sort_values(['count_val', 'contactName'], ascending=False).groupby('contactName').head(1)

        dreams_df['word_amount'] = dreams_df.text.apply(self.get_word_count)
        dreams_df = dreams_df[dreams_df.word_amount < 15]
        dreams_df = dreams_df[['contactName', 'text']]
        dreams_df['count_val'] = dreams_df.groupby(['contactName']).transform('count')
        dreams_df = dreams_df.sort_values(['count_val', 'contactName'], ascending=False).groupby('contactName').head(1)
    
        res_df = dreams_df.loc[dreams_df['contactName'].isin(dreams_df['contactName'].unique()[:8])].append(
            good_night_df.loc[good_night_df['contactName'].isin(good_night_df['contactName'].unique()[:8])])

        return res_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    @staticmethod
    def get_word_count(string):
        return len(string.strip().split())

    def get_dream_messages(self):
        """
        finds messages containing dream words
        :return: dataframe of the data above
        """
        dreams_df = self.contacts_df[['contactName', 'text']]
        dreams_df = dreams_df[self.contacts_df.text.str.lower().str.contains(
            "חלמתי|חלומות|חלמת|dream|dreamt|dreaming|dreams|rêver|rêves|rêvé|rêve|reve|reves|rever|dreamed")]

        for index, row in dreams_df.iterrows():
            if len(row.get_value("text").strip().split()) > 2:
                dreams_df.drop(index, inplace=True)

        # dreams_df['word_count'] = dreams_df.text.apply(self.get_word_count)
        count_series = dreams_df.text.apply(self.get_word_count)
        dreams_df.insert(0, "word_count", count_series)

        dreams_df = dreams_df.sort_values('word_count')
        dreams_df = dreams_df[['contactName', 'text']]
        res_df = dreams_df.tail(5)

        return res_df

    def get_old_messages(self):
        """
        finds old    messages
        :param past_fraction: the fraction part to look at from the oldest msg
        :return: dataframe of the data above
        """
        # noinspection PyTypeChecker
        # past_chats_threshold_days = past_fraction * (
        #     pd.Timestamp(date(datetime.today().year, datetime.today().month, datetime.today().day)).date() - (
        #         min(self.contacts_df.time).date()))
        # past_chats_threshold_date = min(self.contacts_df.time) + to_offset(past_chats_threshold_days)
        # # print(past_chats_threshold_date)
        # df_past_chats = self.contacts_df.where(self.contacts_df.time <= past_chats_threshold_date).dropna()
        # return df_past_chats[['contactName', 'text']]

        word_amount_bounds = (5, 15)
        
        old_messages_df = self.contacts_df[self.contacts_df['contactName'] == self.contacts_df['name']]
        old_messages_df['word_amount'] = old_messages_df.text.apply(self.get_word_count)
        old_messages_df = old_messages_df[old_messages_df.word_amount > word_amount_bounds[0]]
        [old_messages_df.word_amount < word_amount_bounds[1]]
        
        old_messages_df.sort_values(['time'], inplace=True, ascending=False)
        old_messages_df.drop_duplicates("contactName", keep='last', inplace=True)
        
        old_messages_df['just_date'] = pd.to_datetime(old_messages_df['time']).dt.date.astype(str)
        old_messages_df['contactName'] = old_messages_df['contactName'] + '   ' + old_messages_df['just_date']
        
        return old_messages_df[['contactName', 'text']].tail(8)
        
    def get_dreams_or_old_messages(self):
        """
        decides what is better- old msgs or dream msgs and returns it
        :return: json with the data
        """
        # dreams_df = self.get_dream_messages()
        old_messages_df = self.get_old_messages()
        # initial_size = len(dreams_df.index)
        # while initial_size < 5:
            # dreams_df = dreams_df.append(old_messages_df.tail(1))
            # old_messages_df = old_messages_df[:-1]
            # initial_size = len(dreams_df.index)
        # return dreams_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')
        
        # currently returning only old messages - dreams was merged to 'good_night'
        return old_messages_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def get_most_active_groups_and_user_groups(self, max_number_of_groups, max_group_size):
        self.groups_df.sort_values(['totalMessages', 'groupName', 'messagesCount'], ascending=False, inplace=True)
        group_names = self.groups_df.groupName.unique()[:max_number_of_groups]
    
        result_df = self.groups_df.loc[self.groups_df['groupName'].isin(group_names)]
    
        arr_of_df_to_return = []
    
        for group_name in group_names:
            curr_df = result_df[result_df.groupName == group_name]
            group_size = len(curr_df)
    
            # if amount of people in group is smaller than minimum, proceed to next group
            if group_size <= max_group_size:
                arr_of_df_to_return.append(curr_df)
                continue
    
            # narrow the current group to a group of max_group_size people
            jump_size = np.round(group_size / max_group_size)
            # narrowed_df_idx_list = [0, jump_size, 2 * jump_size, 3 * jump_size, 4 * jump_size, group_size - 1]   # 6 people
            narrowed_df_idx_list = [0, jump_size, 2 * jump_size, 3 * jump_size, group_size - 1]                    # 5 people
    
            # for cases the last jump_size equals to last index
            if narrowed_df_idx_list[-2] == narrowed_df_idx_list[-1]:
                narrowed_df_idx_list[-2] -= 1
    
            narrowed_df = curr_df.iloc[narrowed_df_idx_list, :]
    
            # NOW check is used is in narrowed_df, and insert if not
            if not self.user_whatsapp_name in narrowed_df[narrowed_df.groupName == group_name].name.tolist():
    
                # if user isn't in the group at all (even before narrowing), replace with last place
                if not self.user_whatsapp_name in curr_df.name.tolist():
                    # messagesCount and totalMessages are set to 0 since no one cares and they're trimmed anyway
                    narrowed_df = pd.concat([narrowed_df.iloc[:max_group_size-1],
                                             pd.DataFrame([[group_name, self.user_whatsapp_name, 0, 0]],
                                                          columns=narrowed_df.columns)],
                                            ignore_index=True)
    
                # user is in results_df but not in the narrow list, replace with most appropriate one
                else:
                    user_amount_of_msg = int(curr_df[curr_df.name == self.user_whatsapp_name].messagesCount)
                    narrowed_df['diff_msg'] = narrowed_df['messagesCount'] - user_amount_of_msg
                    narrowed_df.sort_values(['diff_msg'], inplace=True, ascending=False)
                    del narrowed_df['diff_msg']
                    narrowed_df = pd.concat([narrowed_df.iloc[:max_group_size-1],
                                             pd.DataFrame(
                                                 [[group_name, self.user_whatsapp_name, user_amount_of_msg, 0]],
                                                 columns=narrowed_df.columns)],
                                            ignore_index=True)
                    narrowed_df.sort_values(['messagesCount'], inplace=True, ascending=False)
    
            arr_of_df_to_return.append(narrowed_df)
    
        result_df = pd.concat([df for df in arr_of_df_to_return])
        sliced_df = result_df[['groupName', 'name']]

        return sliced_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

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

        try:
            # Get name of interesting contact, his messages and the ID of the last message from him
            interesting_message = df.iloc[interesting_message_row_id]
            # print('\nThe interesting message is: {}'.format(interesting_message))
            contact_name_interesting_message = interesting_message['contactName']
            messages_of_contact = df[df.contactName.str.contains(contact_name_interesting_message)]
            index_last_message_from_contact = int(messages_of_contact.tail(1).index.values[0])
        except:

            print("had an exception in get msgs archive")

            # Sort the DataFrame, for usage in future methods
            self.sort()

            resulted_sliced_df = self.contacts_df[["name", "text"]]

            return resulted_sliced_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

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

        # # Get the length of the DataFrame
        # df_len = len(df)
        # half_len = int(df_len/2)
        # # The first and second half of it
        # first_half_df = df.iloc[0:half_len]
        # second_half = df.iloc[half_len:df_len - 1]
        #
        # # Append the first half, interesting messages and then second half
        # df_with_interesting_messages_in_middle = first_half_df.append(interesting_messages, ignore_index=True).append(second_half, ignore_index=True)

        df_with_interesting_messages_on_top = interesting_messages.append(df, ignore_index=True)

        # Sort the DataFrame, for usage in future methods
        self.sort()

        resulted_sliced_df = df_with_interesting_messages_on_top[["name", "text"]]

        return resulted_sliced_df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    @staticmethod
    def convert_whatsapp_time(unix_timestamp):
        str_fixed_date = datetime.fromtimestamp(int(unix_timestamp)).strftime('%H:%M %m/%d/%Y')
        fixed_date = datetime.strptime(str_fixed_date, '%H:%M %m/%d/%Y')

        if fixed_date.date() == date.today():
            return str(fixed_date.time())
        elif fixed_date.date() == date.today() - timedelta(1):
            return 'Yesterday'
        else:
            import calendar
            return calendar.day_name[fixed_date.weekday()]


    def get_k_latest_chats(self, scraper, k=6):
        df = scraper.get_k_latest_chats(k)
        df.time = df.time.apply(self.convert_whatsapp_time)
        return df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def _get_conversation_rank(self, conv):
        return 1

    def get_k_most_interesting(self, df, k=1):
        # todo implement the shit out of it
        # todo maybe only conversations older than... (real new ones are not as long as)
        # todo maybe define 'conversation' between close times
        # df.to_csv('interesting20.csv')
        ranks = []
        for conv_id, conversation in df.groupby('conv_id'):
            ranks.append( (conv_id, self._get_conversation_rank(conversation)) )

        ranks = sorted(ranks, key=lambda x: x[1])       # [(conv_id, rank)...(conv_id, rank)]
        if k == 1:
            return df[df.conv_id == ranks[0][0]].loc[:,['contactName','text']]
        else:
            return df[df.conv_id == ranks[:k][0]].loc[:, ['contactName', 'text']]

    def create_world_df(self, world_name, scraper, override_keywords=False):
        # get keywords and amount from protocol file
        with open('search_protocols/search_protocol_' + self.user_language, 'r', encoding='utf8') as f:
            for line in f:
                l = line.strip().split('|')
                if l[0] == world_name:
                    keywords = override_keywords+l[1].split(',') if override_keywords else l[1].split(',')
                    amount = int(l[2])
                    min_msg_len = int(l[3])
                    get_msg_env = True if l[4] == 'true' else False
                    after_competition = False if l[5] == 'false' else int(l[6])
                    is_incoming_only = True if l[7] == 'true' else False
                    is_unique = True if l[8] == 'true' else False
                    is_contacts_only = True if l[9] == 'true' else False
                    break

        cur_amount = 0
        keyword_idx = 0
        dfs_arr = []
        people = []

        while cur_amount < amount:
            try:
                cur_df, real_amount, people = scraper.search(
                    keywords[keyword_idx], amount, min_msg_len, cur_amount, is_incoming_only, is_unique, people, is_contacts_only, get_msg_env)
            except IndexError:      # end of keywords list
                with open('search_protocols/search_protocol_' + self.user_language, 'r', encoding='utf8') as f:
                    keyword_idx = 0
                    for line in f:
                        l = line.split('|')
                        if l[0] == 'backup':
                            keywords = l[1].split(',')
                continue
            if not cur_df.empty:
                dfs_arr.append(cur_df)
            cur_amount += real_amount
            keyword_idx += 1

        df = pd.concat([df for df in dfs_arr])
        df = df if not after_competition else self.get_k_most_interesting(df, k=after_competition)
        return df.to_json(date_format='iso', double_precision=0, date_unit='s', orient='records')

    def create_db_using_search(self, scraper):
        # self.latest_chats = self.get_k_latest_chats(scraper, k=6)
        self.my_name_messages = self.create_world_df('my_name', scraper, override_keywords=[self.user_nickname, self.user_first_name])
        # self.amphi_data = self.get_k_latest_chats(scraper, k=40)
        # self.good_night_messages = self.create_world_df('good_night', scraper)
        # self.dreams_or_old_messages = self.create_world_df('dreams', scraper)
        # self.most_interesting = self.create_world_df('interesting_chat', scraper)
        # self.love_messages = self.create_world_df('love', scraper)        # not for v.Liege