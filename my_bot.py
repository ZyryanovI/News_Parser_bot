import telebot
import db_requests
import collections
from user import *

TOKEN = '523428665:AAHYV1_YOHFZYwrHrvlpWkaCaWQ7q9LlbLE'

DEFAULT_DOCS_AMOUNT = 5  # число свежих новостей по умолчанию
DEFAULT_TOPICS_AMOUNT = 5  # число свежих тем по умолчанию
DEFAULT_WORDS_AMOUNT = 5  # количество слов, лучше всего описывающих тему

bot = telebot.TeleBot(TOKEN)

requests_dict = collections.defaultdict()

command_dict = {'new_docs': 'new_docs_(message.chat.id, args)',
                'new_topics': 'new_topics_(message.chat.id, args)',
                'topic': 'topic_(message.chat.id, args)',
                'doc': 'doc_(message.chat.id, args)',
                'words': 'words_(message.chat.id, args)',
                'describe_doc': 'describe_doc_(message.chat.id, args)',
                'describe_topic': 'describe_topic_(message.chat.id, args)'}



def set_user(cur_id):
    '''
    Добавляем нового пользователя
    :param cur_id: id пользователя
    '''
    if cur_id in requests_dict.keys():
        return
    else:
        requests_dict[cur_id] = user(cur_id)


def message_to_user(message, info, status):
    '''
    Функция, общающаяся с пользователем
    :param message: сообщение пользователя
    :param info: то, что мы говорим пользователю
    :param status: новый статус пользователя
    :return:
    '''
    set_user(message.chat.id)
    bot.send_message(message.chat.id, info)
    requests_dict[message.chat.id] = status


def set_status_and_get_arg(message):
    '''
    Функция, выделяющая команду и аргумент команды отдельно
     и ставящая статус пользователю
    :param message:
    :return: аргументы
    '''
    set_user(message.chat.id)
    status = message.text.split()[0][1:]
    args = message.text.replace('/' + status, '').strip()
    requests_dict[message.chat.id] = status
    return args


@bot.message_handler(commands=['start'])
def start(message):
    '''
    Вывод приветствия
    :param message:
    :return:
    '''
    message_to_user(message, 'Hi! For help write /help', 'start')


@bot.message_handler(commands=['help'])
def help(message):
    '''
    Вывод информации по использованию бота
    :param message:
    :return:
    '''
    message_to_user(message, 'There are several opportunities:\n' +
                     '/help - opportunities\n' +
                     '/new_docs <N> - the latest N news\n' +
                     '/new_topics <N> - the latest N topics\n' +
                     '/topic <topic_name> - description of the topic\n' +
                     '/doc <doc_title> - text of the document\n' +
                     '/words <topic_name> - best 5 words to describe the topic\n' +
                     '/describe_doc <doc_title> - document statistics\n' +
                     '/describe_topic <topic_name> - topic statistics', 'start')


def new_docs_(message_chat_id, number):
    '''
    ОТправляем пользователю определенное количество новостей
    :param message_chat_id: id пользователя
    :param number: требуемое количество новостей
    '''
    if number.isdigit():
        number = int(number)
        if number > 0:
            docs = db_requests.get_new_news(number)
            num_counter = 1
            for i in docs:
                bot.send_message(message_chat_id, str(num_counter) + ') ' +
                                 i.title + '\n' + i.URL)
                num_counter += 1
            requests_dict[message_chat_id] = 'start'
        elif number == 0:
            bot.send_message(message_chat_id, "But why did you ask me to do that"
                                              " if you want to see nothing?"
                                              " Here is your nothing, your are welcome.")
        else:
            bot.send_message(message_chat_id, "A negative number? Really?"
                                              " Enter something normal, ok?")
    else:
        bot.send_message(message_chat_id, "Hm..., it seems like that is not number,"
                                          " enter something else")


def new_topics_(message_chat_id, number):
    '''
    Отправляем пользователю определенное количество тем
    :param message_chat_id: id пользователя
    :param number: тебуемое количество тем
    :return:
    '''
    if number.isdigit():
        number = int(number)
        if number > 0:
            topics = db_requests.get_new_topics(number)
            num_counter = 1
            for i in topics:
                bot.send_message(message_chat_id, str(num_counter) + ') ' +
                                 i.name + '\n' + i.URL)
                num_counter += 1
            requests_dict[message_chat_id] = 'start'
        elif number == 0:
            bot.send_message(message_chat_id, "nothing so nothing ¯\_(ツ)_/¯")
        else:
            bot.send_message(message_chat_id, 'this number is negative, '
                                              'try again please')
    else:
        bot.send_message(message_chat_id, "Hm..., it seems like that is not number,"
                                          " enter something else")


def topic_(message_chat_id, name):
    '''
    Отправляет описание определенной темы
    :param message_chat_id: id пользователя
    :param name: название темы
    '''
    topic_description = db_requests.get_topics_description(name)
    if topic_description is None:
        bot.send_message(message_chat_id, "Enter correct topic name")
    else:
        bot.send_message(message_chat_id, topic_description)
        fresh_docs = db_requests.get_topic_new_news(name, DEFAULT_DOCS_AMOUNT)
        num_counter = 1
        for i in fresh_docs:
            bot.send_message(message_chat_id, str(num_counter) + ') ' +
                             i.title + '\n' + i.URL)
            num_counter += 1
        requests_dict[message_chat_id] = 'start'


def doc_(message_chat_id, name):
    '''
    Отправляем тест документа
    :param message_chat_id: id пользователя
    :param name: название документа
    '''
    cur_text = db_requests.get_docs_text(name)

    if cur_text is None:
        bot.send_message(message_chat_id, "Enter real doc name, please")
    else:
        bot.send_message(message_chat_id, cur_text)
        requests_dict[message_chat_id] = 'start'


def words_(message_chat_id, name):
    '''
    Вывод 5 слов, лучше всего описывающих тему
    :param message_chat_id: id пользователя
    :param name: название темы
    :return:
    '''
    tegs = db_requests.get_words(name, DEFAULT_WORDS_AMOUNT)

    if tegs is None:
        bot.send_message(message_chat_id, "It is quite hard to find best 5 words, "
                                          "if name is incorrect")
    else:
        bot.send_message(message_chat_id, ', '.join(tegs))
        requests_dict[message_chat_id] = 'start'


def describe_doc_(message_chat_id, name):
    '''
    Описание документов путем построения графиков
    :param message_chat_id: id пользователя
    :param name: название документа
    :return:
    '''
    plot_f_name = 'p1ot_doc_' + str(message_chat_id) + '_f.png'
    plot_l_name = 'plot_doc_' + str(message_chat_id) + '_l.png'
    if db_requests.make_final_plots(name, 'document',
                                    plot_f_name, plot_l_name):
        plot_f = open(plot_f_name, 'rb')
        bot.send_photo(message_chat_id, plot_f)
        plot_l = open(plot_l_name, 'rb')
        bot.send_photo(message_chat_id, plot_l)

        requests_dict[message_chat_id] = 'start'
    else:
        bot.send_message(message_chat_id, "Something went wrong,"
                                          " try to enter correct document name")


def describe_topic_(message_chat_id, name):
    '''
    Описание темы, путем графиков
    :param message_chat_id: id пользователя
    :param name: название темы
    :return:
    '''
    plot_f_name = 'p1ot_top_' + str(message_chat_id) + '_f.png'
    plot_l_name = 'plot_top_' + str(message_chat_id) + '_l.png'
    if db_requests.make_final_plots(name, 'topic',
                                    plot_f_name, plot_l_name):
        cur_dict = db_requests.get_doc_number_and_avg_len(name)
        bot.send_message(message_chat_id, "Documents amount: " +
                         str(cur_dict['doc_number']) + '\n' + "Average length: " +
                         str(cur_dict['avg_len']))

        plot_f = open(plot_f_name, 'rb')
        bot.send_photo(message_chat_id, plot_f)
        plot_l = open(plot_l_name, 'rb')
        bot.send_photo(message_chat_id, plot_l)

        requests_dict[message_chat_id] = 'start'
    else:
        bot.send_message(message_chat_id, "Something went wrong,"
                                          " maybe your topic name was incorrect,"
                                          " try again please")


@bot.message_handler(commands=['new_docs', 'new_topics', 'topic',
                                    'words', 'doc', 'describe_doc',
                                    'describe_topic'])
def text(message):
    '''
    обработка сообщений начинающихся с команды
    :param message:
    :return:
    '''
    args = set_status_and_get_arg(message)
    exec(command_dict[requests_dict[message.chat.id]])
    #  exec()


@bot.message_handler(content_types=['text'])
def answer(message):
    '''
    Обработка сообщений без команды
    :param message:
    :return:
    '''
    message_to_user(message, 'Sorry, I am not very talkative, '
                                      'I prefer to do commands and show '
                                      'something about the news. '
                                      'Maybe you should try to write /help '
                                      'to understand how to use me. Good luck',
                    'start')


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except RuntimeError:
            pass
