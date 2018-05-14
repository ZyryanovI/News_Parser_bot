import telebot
import db_requests
import collections
from user import *

TOKEN = '523428665:AAHYV1_YOHFZYwrHrvlpWkaCaWQ7q9LlbLE'

bot = telebot.TeleBot(TOKEN)

requests_dict = collections.defaultdict()


def set_user(cur_id):
    if cur_id in requests_dict.keys():
        return
    else:
        requests_dict[cur_id] = user(cur_id)


@bot.message_handler(commands=['start'])
def start(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, 'Hi! For help write /help')
    requests_dict[message.chat.id] = 'start'


@bot.message_handler(commands=['help'])
def help(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, 'There are several opportunities:\n' +
                     '/help - opportunities\n' +
                     '/new_docs - the latest news\n' +
                     '/new_topics - the latest topics\n' +
                     '/topic - description of the topic\n' +
                     '/doc - text of the document\n' +
                     '/words - best 5 words to describe the topic\n' +
                     '/describe_doc - document statistics\n' +
                     '/describe_topic - topic statistics')
    requests_dict[message.chat.id] = 'help'


@bot.message_handler(commands=['new_docs'])
def new_docs(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, 'How many docs do you want?')
    requests_dict[message.chat.id] = 'new_docs'


@bot.message_handler(commands=['new_topics'])
def new_topics(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, 'How many topics do you want?')
    requests_dict[message.chat.id] = 'new_topics'


@bot.message_handler(commands=['topic'])
def topic(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, 'Description of what topic do you want?')
    requests_dict[message.chat.id] = 'topic'


@bot.message_handler(commands=['doc'])
def doc(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, "Which document text do you want to see?")
    requests_dict[message.chat.id] = 'doc'


@bot.message_handler(commands=['words'])
def words(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, "Words from which topic do you want?")
    requests_dict[message.chat.id] = 'words'


@bot.message_handler(commands=['describe_doc'])
def describe_doc(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, "Statistics for which document do you want?\n"
                                      "And are you sure that you want?\n"
                                      "There will be a looooooooooot of numbers")
    requests_dict[message.chat.id] = 'describe_doc'


@bot.message_handler(commands=['describe_topic'])
def describe_topic(message):
    set_user(message.chat.id)
    bot.send_message(message.chat.id, "Statistics for which topic do you want?"
                                      "And are you sure that you want?\n"
                                      "There will be a looooooooooot of numbers")
    requests_dict[message.chat.id] = 'describe_topic'


@bot.message_handler(content_types=['text'])
def text(message):
    set_user(message.chat.id)

    if requests_dict[message.chat.id] == 'new_docs':
        if message.text.isdigit():
            number = int(message.text)
            if number > 0:
                docs = db_requests.get_new_news(number)
                num_counter = 1
                for i in docs:
                    bot.send_message(message.chat.id, str(num_counter) + ') ' +
                                     i.title + "\n" + i.URL)
                    num_counter += 1
                requests_dict[message.chat.id] = 'start'

            elif number == 0:
                bot.send_message(message.chat.id, "But why did you ask me"
                                                  " to do that if you want to see nothing?"
                                                  "Here is your nothing, your are welcome.")
            else:
                bot.send_message(message.chat.id, "A negative number? Really?"
                                                  " Enter something normal, ok?")
        else:
            bot.message_handler(message.chat.id, "Hm..., it seems like that is not number"
                                                 "enter something else or convince me that this is a number."
                                                 " I'm kidding, don't even try, I do not care, do it again")

    elif requests_dict[message.chat.id] == 'new_topics':
        if message.text.isdigit():
            number = int(message.text)
            if number > 0:
                topics = db_requests.get_new_topics(number)
                num_counter = 1
                for i in topics:
                    bot.send_message(message.chat.id, str(num_counter) + ') ' +
                                     i.name + '\n' + i.URL)
                    num_counter += 1
                requests_dict[message.chat.id] = 'start'
            elif number == 0:
                bot.send_message(message.chat.id, "nothing so nothing ¯\_(ツ)_/¯")
            elif number < 0:
                bot.send_message(message.chat.id, "this number is negative, "
                                                  "the same as my opinion of you from this moment")

        else:
            bot.send_message(message.chat.id, "That is not number, "
                                              "my dear friend, you should know that")

    elif requests_dict[message.chat.id] == 'topic':
        topic_description = db_requests.get_topics_description(message.text)
        if topic_description is None:
            bot.send_message(message.chat.id, "Enter correct topic name")
        else:
            bot.send_message(message.chat.id, topic_description)
            fresh_docs = db_requests.get_topic_new_news(message.text, 5)
            num_counter = 1
            for i in fresh_docs:
                bot.send_message(message.chat.id, str(num_counter) + ') ' +
                                 i.title + '\n' + i.URL)
                num_counter += 1
            requests_dict[message.chat.id] = 'start'

    elif requests_dict[message.chat.id] == 'doc':
        cur_text = db_requests.get_docs_text(message.text)

        if cur_text is None:
            bot.send_message(message.chat.id, "Enter real doc name, please")
        else:
            bot.send_message(message.chat.id, cur_text)
            requests_dict[message.chat.id] = 'start'

    elif requests_dict[message.chat.id] == 'words':
        tegs = db_requests.get_words(message.text, 5)

        if tegs is None:
            bot.send_message(message.chat.id, "It is quite hard to find best 5 words, "
                                              "if name is incorrect")
        else:
            bot.send_message(message.chat.id, ' '.join(tegs))
            requests_dict[message.chat.id] = 'start'

    elif requests_dict[message.chat.id] == 'describe_doc':
        stat_info = db_requests.get_doc_statistic(message.text)

        if stat_info is None:
            bot.send_message(message.chat.id, "It seems like there is no such doc :("
                                              "or it is weird empty doc")
        else:
            description_text = "frequency distribution: " + "\n" +\
                               " ".join(stat_info[0]) + "\n" + "length distribution: " +\
                               "\n" + " ".join(stat_info[1])
            bot.send_message(message.chat.id, description_text)
            requests_dict[message.chat.id] = 'start'

    elif requests_dict[message.chat.id] == 'describe_topic':
        stat_info = db_requests.get_topic_statistic(message.text)
        if stat_info is None:
            bot.send_message(message.chat.id, "This topic has no docs,"
                                              "so I can't make description.")
        else:
            description_text = "docs number: " + " ".join(stat_info[0]) + "\n" +\
                               "average_document_length: " + " ".join(stat_info[1]) +\
                               '\n' + "frequency distribution: " + '\n' +\
                               " ".join(stat_info[2] + '\n' + "length distribution: " +
                                        '\n' + " ".join(stat_info[3]))
            bot.send_message(message.chat.id, description_text)
            requests_dict[message.chat.id] = 'start'

    else:
        bot.send_message(message.chat.id, "Please write something correct")


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            pass
