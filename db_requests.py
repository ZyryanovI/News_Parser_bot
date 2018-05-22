import peewee
import collections
from Data_Base import *
import matplotlib
import pandas
import json
from matplotlib import pyplot

MAX_NUMBER_OF_OCCURRENCES = 14
MIN_NUMBER_OF_OCCURRENCES = 2


def get_new_news(number):
    '''
    Получить number свежих новостей
    :param number: - требуемое количество новостей
    :return: список из number элементов Document, которые первые при сортировке
    '''
    res = []
    for doc in Documents.select().order_by(-Documents.last_update):
        res.append(doc)

    return res[:number]


def get_new_topics(number):
    '''
    Получить number свежих тем
    :param number: требуемое количество тем
    :return: список из number элементов типа Topic, которые первые при сортировке
    '''
    new_topics = Topics.select().join(Documents).\
        where(Topics.name == Documents.topic_
              and Documents.last_update ==
              Documents.select(peewee.fn.
                               Max(Documents.last_update)).
              where(Documents.topic_ ==
                    Topics.name)).order_by(-Documents.last_update)
    res = []
    for cur_topic in new_topics:
        res.append(cur_topic)

    return res[:number]


def get_topics_description(name_of_topic):
    '''
    Получение описания темы
    :param name_of_topic: название темы
    :return: описание темы, или Node, если такой темы не существует
    '''
    cur_topic = Topics.select().where(Topics.name == name_of_topic)
    if len(cur_topic) > 0:
        return cur_topic.get().description
    else:
        return None


def get_topic_new_news(name_of_topic, number):
    '''
    Получение number свежих новостей для темы
    :param name_of_topic: название темы
    :param number: запрашиваемое количество новостей
    :return: Список из number объектов Document или None, если такой темы нет
    '''
    cur_topic = Topics.select().where(Topics.name == name_of_topic)

    if len(cur_topic) > 0:
        res = []
        for news in Documents.select().where(Documents.topic_ ==
                                             name_of_topic).order_by(-Documents.last_update):
            res.append(news)
        return res[:number]
    else:
        return None


def get_docs_text(doc_name):
    '''
    Получаем текст данного документа
    :param doc_name: Название документа
    :return: текст документа или None, если такого документа нет
    '''
    cur_topic = Documents.select().where(Documents.title == doc_name)

    if len(cur_topic) > 0:
        return cur_topic.get().text

    else:
        return None


def get_words(name_of_topic, number):
    '''
    Получаем number слов, лучше всего описывающих тему
    :param name_of_topic: название темы
    :param number: количество слов
    :return:
    '''
    cur_topics = Topics.select().where(Topics.name == name_of_topic)

    if len(cur_topics) > 0:
        cur_docs = Documents.select().where(Documents.topic_ ==
                                            Topics.select().where(Topics.name == cur_topics))
        tegs_dict = collections.defaultdict(int)
        for doc in cur_docs:
            cur_tegs = Teg.select().where(Teg.document_ == doc)
            for teg in cur_tegs:
                tegs_dict[teg.name] += 1

        res = []
        for teg in tegs_dict:
            res.append(teg)

        res.sort(key=(lambda teg: -tegs_dict[teg]))

        return res[:number]

    else:
        return None


def get_doc_description(doc_name, file_name):
    pass


def make_plot(data_dict, plot_name, x_name, y_name):
    '''
    Создает график
    :param data_dict: данные
    :param plot_name: название графика
    :param x_name: название оси x
    :param y_name: название оси y
    :return: график
    '''
    data_frame = pandas.DataFrame(data_dict)
    my_plot = data_frame.plot(kind="bar", title=plot_name,
                              colormap='jet', legend=None)
    my_plot.set_xlabel(x_name)
    my_plot.set_ylabel(y_name)
    return my_plot


def make_final_plots(name, type, file_name_f, file_name_l):
    '''
    Создание графиков для документа или темы
    :param name: название документа или темы
    :param type: тип, то есть 'topic' или 'document'
    :param file_name_f: файл для графика распределения частот
    :param file_name_l: файл для графика распределения длин
    :return: False - если по какой-то причине создать не удалось,
     True - если все хорошо
    '''
    if type == 'topic':
        stat = TopicStatistic.select().where(TopicStatistic.topic_ ==
                                             Topics.select().
                                             where(Topics.name == name))
    elif type == 'document':
        stat = DocumentStatistic.select().where(DocumentStatistic.document_ ==
                                                Documents.select().
                                                where(Documents.title == name))
    else:
        return False

    if len(stat) > 0:
        freq_distr = stat.get().frequency_distribution
        make_plot([0] + json.loads(freq_distr)
                  [MIN_NUMBER_OF_OCCURRENCES:MAX_NUMBER_OF_OCCURRENCES],
                  "Frequency distribution", "word frequency",
                  "amount of words with such frequency")
        matplotlib.pyplot.savefig(file_name_f)

        len_distr = stat.get().length_distribution
        make_plot(json.loads(len_distr), "Length distribution",
                  "word length", "amount of words with such len")
        matplotlib.pyplot.savefig(file_name_l)
        matplotlib.pyplot.close()

        return True

    else:
        return False


def get_doc_number_and_avg_len(name):
    '''
    Функция, возвращающая кол-во документов в теме и среднюю длину
    :param name: название темы
    '''
    stat = TopicStatistic.select().\
        where(TopicStatistic.topic_ ==
              Topics.select().where(Topics.name == name))
    if len(stat) > 0:
        return {'avg_len': stat.get().average_length,
                'doc_number': stat.get().documents_number}
    else:
        return None
