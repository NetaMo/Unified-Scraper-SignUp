import json


def test_data_analysis(DB):
    """
    print all of the data analysis methods output
    :param DB: the WhatsAppDB to test
    """
    print("FinishedWhatsAppHandler")

    print("=============================================")
    print("contacts_df:")
    print(DB.contacts_df)
    print("=============================================")

    print("=============================================")
    print("groups_df:")
    print(DB.groups_df)
    print("=============================================")

    # print("Me:")
    # print(DB.contacts_df[DB.contacts_df["name"] == 'Me'])
    # print("=============================================")

    print("get_last_chats")
    print(json.loads(DB.get_latest_chats(6)))
    print("----------------------------------")

    print("get_closest_persons_and_msg")
    number_of_contacts = 150
    past_fraction = 0.75
    print(json.loads(DB.get_closest_persons_and_msg(number_of_contacts, DB.user_name, past_fraction)))
    print("----------------------------------")

    print("does_df_has_hebrew")
    print(DB.does_df_has_hebrew())
    print("----------------------------------")

    print("get_good_night_messages")
    print(json.loads(DB.get_good_night_messages()))
    print("----------------------------------")

    print("get_dreams_or_old_messages")
    past_fraction = 0.25
    print(json.loads(DB.get_dreams_or_old_messages(past_fraction)))
    print("----------------------------------")

    # print("get_most_active_groups_and_user_groups")
    # max_num_of_groups = 5
    # print(json.loads(DB.get_most_active_groups_and_user_groups(max_num_of_groups)))
    # print("----------------------------------")

    print("get_chat_archive")
    print(json.loads(DB.get_chat_archive()))
    print("----------------------------------")