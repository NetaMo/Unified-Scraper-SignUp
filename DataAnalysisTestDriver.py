import json

import WhatsAppWebScraper


def test_data_analysis(DB):
    """
    print all of the data analysis methods output for analysis.
    :param DB: the WhatsAppDB to test
    """

    # print("=============================================")
    # print("contacts_df:")
    # print(DB.contacts_df)
    # print("=============================================")
    #
    # print("=============================================")
    # print("groups_df:")
    # print(DB.groups_df)
    # print("=============================================")

    # print("get_chat_archive")
    # print(DB.get_chat_archive())
    # print("----------------------------------\n")

    print()
    print("----------------------------------\n")
    # print("get_last_chats")
    print("These are the first 6 people you talked to - this does not include groups!\n")
    for i in json.loads(DB.latest_chats):
        print("\t{0}".format(i["contactName"]))
        for j in i["text"].split("\n"):
            print("\t\t{0}".format(j))
    print()
    print("----------------------------------\n")

    print("These are the 40 people you talked to the most and one message from each.\n")
    for i in json.loads(DB.closest_persons_and_msg):
        print("\t{0}".format(i["contactName"]))
        for j in i["text"].split("\n"):
            print("\t\t{0}".format(j))
    print()
    print("----------------------------------\n")

    print("some info\n")
    print(json.loads(DB.have_hebrew))
    print()
    print("----------------------------------\n")

    print("Messages containing the words good night.\n")
    for i in json.loads(DB.good_night_messages):
        print("\t{0}".format(i["contactName"]))
        for j in i["text"].split("\n"):
            print("\t\t{0}".format(j))
    print()
    print("----------------------------------\n")

    print("Messages containing the words dream or very old messages.\n")
    for i in json.loads(DB.dreams_or_old_messages):
        print("\t{0}".format(i["contactName"]))
        for j in i["text"].split("\n"):
            print("\t\t{0}".format(j))
    print()
    print("----------------------------------\n")

    max_num_of_groups = 5
    print("These are the " + str(max_num_of_groups) + " groups you talk to the most sorted by "
                                                      "activity, and the people in each group are "
                                                      "also sorted by number of messages they sent.")
    groups = []
    for i in json.loads(DB.most_active_groups_and_user_groups):
        if i["groupName"] not in groups:
            groups += [i["groupName"]]
            print("\n\t{0}".format(i["groupName"]))
        print("\t\t{0}".format(i["name"]))
    print()
    print("----------------------------------")
