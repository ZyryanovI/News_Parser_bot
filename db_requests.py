import peewee
import collections
from Data_Base import *


def get_new_news(number):

    res = []
    for doc in Documents.select().order_by(-Documents.last_update):
        res.append(doc)

    return res[:number]


def get_new_topics(number):

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
    cur_topic = Topics.select().where(Topics.name == name_of_topic)
    if len(cur_topic) > 0:
        return cur_topic.get().description
    else:
        return None


def get_topic_new_news(name_of_topic, number):
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
    cur_topic = Documents.select().where(Documents.title == doc_name)

    if len(cur_topic) > 0:
        return cur_topic.get().text

    else:
        return None


def get_docs_number(name_of_topic):
    stat = TopicStatistic.select().where(TopicStatistic.topic_ == Topics.
                                         select().where(Topics.name == name_of_topic).name)

    if len(stat) > 0:
        return stat.get().documents_number
    else:
        return None


def get_averenge_doc_len(name_of_topic):
    stat = TopicStatistic.select().where(TopicStatistic.topic_ ==
                                         Topics.select().where(Topics.name == name_of_topic).name)

    if len(stat) > 0:
        return stat.get().average_length
    else:
        return None


def get_words(name_of_topic, number):
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


def get_topic_statistic(name_of_topic):
    cur_statistic = TopicStatistic.select().where(TopicStatistic.topic_ == Topics.
                                         select().where(Topics.name == name_of_topic))

    if len(cur_statistic) > 0:
        return [cur_statistic.get().frequency_distribution, cur_statistic.get().length_distribution]
    else:
        return None


def get_doc_statistic(name_of_doc):
    cur_statistic = DocumentStatistic.select().where(DocumentStatistic.
                                                     document_ == Documents.select().
                                                     where(Documents.title == name_of_doc))

    if len(cur_statistic) > 0:
        return [cur_statistic.get().frequency_distribution, cur_statistic.get().length_distribution]
    else:
        return None
