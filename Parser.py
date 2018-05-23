import re
import requests
from bs4 import BeautifulSoup
import dateparser
import collections
import json
from Data_Base import *
import locale

MAX_REDIRECTS = 50  # максимальное кол-во перенаправлений
DEVIATION_CONST = 3  # константа, учитывающаяся при выборе слов,
#  попадающих в отклонение


class Parser:

    def __init__(self, new_link):
        self.link = new_link
        self.up_topics = set()  # запоминае тем, нуждающихся в обновлении

    def get_deviation(self, entrance_of_word):
        '''
        Функция поиска среднеквадратичного отклонения
        :param entrance_of_word: словарь вхождения слов
        :return: отклонение
        '''
        avg_entrence_number = sum(entrance_of_word.values()) / len(entrance_of_word)
        deviation = 0
        for cur_word in entrance_of_word:
            deviation += (avg_entrence_number - entrance_of_word[cur_word])**2
        deviation = (deviation/len(entrance_of_word))**0.5
        return deviation

    def parse_topics(self):
        '''
        Парсим темы и добавляем их базу данных при необходимости
        :return:
        '''
        session = requests.Session()
        session.max_redirects = MAX_REDIRECTS
        cur_data = BeautifulSoup(session.get(self.link).text, 'lxml')

        # берем все темы
        topics = cur_data.find_all('div', {'class': 
                                               'item item_story js-story-item'})
        for cur_topic_ in topics:

            cur_name = cur_topic_.find('span', 
                                       {'class': 'item__title'}).\
                text.strip()
            cur_URL = cur_topic_.find('a', 
                                      {'class': 'item__link no-injects'})['href'].\
                strip()
            cur_description = cur_topic_.find('span', 
                                              {'class': 'item__text'}).\
                text.strip()

            print(cur_name)

            if len(Topics.select().where(cur_URL == Topics.URL)) < 1:
                Topics.create(name=cur_name, URL=cur_URL, 
                              description=cur_description)

    def get_text_and_tags_from_doc(self, new_url):
        '''
        Получаем текст и теги
        :param new_url: ссылка статьи
        :return: словарь, где по 'text' находится текст,
        а по 'tegs' - кортеж их текстов тегов
        '''
        session = requests.Session()

        session.max_redirects = MAX_REDIRECTS

        cur_data = BeautifulSoup(session.get(new_url).text, 'lxml')

        paragraphs = cur_data.find_all('p')

        res_par = map((lambda cur_paragraph: str(cur_paragraph.text)), paragraphs)
        text = ' '.join(res_par)
        # У некоторых новостей другая html-разметка, тогда парсим по ней
        if len(text) == 0:
            paragraphs = cur_data.find_all('div', {'class': 'article__text'})
            res_par = map((lambda cur_paragraph: cur_paragraph.text), paragraphs)
            text = ' '.join(res_par)
        tegs = cur_data.find_all('', {'class': 'article__tags__link'})
        return {'text': text, 
                'tegs': tuple(map((lambda cur_teg: cur_teg.text), tegs))}

    def parse_documents(self, name_of_topic):
        '''
        Парсим документы для темы, при необходимости добавляем в бд
        :param name_of_topic: названием темы
        :return:
        '''
        topics = Topics.select().where(Topics.name == name_of_topic)

        if len(topics) == 0:
            return
        else:
            session = requests.Session()
            session.max_redirects = MAX_REDIRECTS
            cur_topic_url = topics.get().URL

            cur_data = BeautifulSoup(session.get(cur_topic_url).text, 'lxml')
            documents = cur_data.find_all('div',
                                          {'class': 
                                               'item item_story-single js-story-item'})

            for doc in documents:
                cur_name = doc.find('span', {'class': 'item__title'}).text.strip()
                cur_URL = doc.find('a',
                                   {'class': 'item__link no-injects js-yandex-counter'})['href'].strip()
                locale.setlocale(locale.LC_ALL, 'russian')
                last_update = dateparser.\
                    parse(doc.find('span', {'class': 'item__info'}).text,
                          languages=['ru'])

                # проверяем, что у нас нет документа с таким url
                if len(Documents.select().where(Documents.URL == cur_URL
                                                and Documents.last_update == last_update)) < 1:
                    # запоминаем, что необходимо пересчитать статистику по теме
                    self.up_topics.add(name_of_topic)

                    # удаляем теги, т.к. могли поменяться
                    Teg.delete().where(Teg.document_ == Documents.
                                       select().where(Documents.URL == cur_URL)).execute()

                    # удаляем предыдущую статистику
                    DocumentStatistic.delete().where(DocumentStatistic.document_ == Documents.
                                                     select().where(Documents.URL == cur_URL)).execute()

                    Documents.delete().where(Documents.URL == cur_URL).execute()

                    cur_top = Topics.select().where(Topics.name == name_of_topic).get()
                    cur_page = self.get_text_and_tags_from_doc(cur_URL)
                    cur_text = cur_page['text']

                    new_document = Documents(topic_=cur_top,
                                             title=cur_name,
                                             URL=cur_URL,
                                             last_update=last_update,
                                             text=cur_text)

                    new_document.save()

                    self.save_doc_statistic(new_document)

                    for cur_teg in cur_page['tegs']:
                        Teg.create(document_=new_document,
                                   name=cur_teg)

    #  ***********************************************************************************

    def find_statistic(self, text):  # доделать
        words = re.findall(r'[\w,-]+', text)
        lengths = collections.defaultdict(int)
        entrance_of_frequencies = collections.defaultdict(int)
        entrance_of_word = collections.defaultdict(int)

        for cur_word in words:
            entrance_of_word[cur_word] += 1
            lengths[len(cur_word)] += 1

        cur_deviation = self.get_deviation(entrance_of_word)
        avg_number = sum(entrance_of_word.values()) / len(entrance_of_word)

        for cur_word in entrance_of_word:
            if (DEVIATION_CONST*cur_deviation >= abs(entrance_of_word[cur_word]
                                                     - avg_number)):
                entrance_of_frequencies[entrance_of_word[cur_word]] += 1

        enter_list = [0]*(max(entrance_of_frequencies.keys())+1)
        len_list = [0]*(max(lengths.keys())+1)

        for cur_ent in entrance_of_frequencies:
            enter_list[cur_ent] = entrance_of_frequencies[cur_ent]

        for cur_len in lengths:
            len_list[cur_len] = lengths[cur_len]

        res = [enter_list, len_list]

        return res

    def save_doc_statistic(self, doc):
        '''
        Сохраняем статистику для документа
        :param doc: название документа
        :return:
        '''
        try:
            stat = self.find_statistic(doc.text)
            DocumentStatistic.create(document_=doc,
                                     frequency_distribution=json.dumps(stat[0]),
                                     length_distribution=json.dumps(stat[1]))
        except ValueError:
            print("Something wrong with save_doc_statistic")

    def add_distribution(self, distribution, adding_distribution):
        for i in range(len(adding_distribution)):
            if i >= len(distribution):
                distribution += [adding_distribution[i]]
            else:
                distribution[i] += adding_distribution[i]

    def save_topic_stat(self, name_of_topic):
        '''
        Сохраняем статистику по теме
        :param name_of_topic: навзание темы
        :return:
        '''
        documents = Documents.select().where(Documents.topic_ ==
                                             Topics.select().where(Topics.name ==
                                                                   name_of_topic))
        averege_len = 0
        if len(documents) == 0:
            print("some document is empty")
        else:
            for document in documents:
                averege_len += len(re.findall(r'[\w,-]+', document.text))

            averege_len /= len(documents)

            text = ' '.join(document.text for document in documents)

            statistic = self.find_statistic(text)
            TopicStatistic.create(topic_=Topics.select().
                                  where(Topics.name == name_of_topic).get(),
                                  documents_number=len(documents),
                                  average_length=averege_len,
                                  frequency_distribution=json.dumps(statistic[0]),
                                  length_distribution=json.dumps(statistic[1]))


if __name__ == '__main__':
    data_base.connect()
    data_base.create_tables([Documents, Teg, Topics,
                             DocumentStatistic, TopicStatistic])

    my_parser = Parser("https://www.rbc.ru/story/")

    my_parser.parse_topics()

    for cur_topic in Topics.select():

        print(cur_topic)

        my_parser.parse_documents(cur_topic.name)

    for topic_name in my_parser.up_topics:
        TopicStatistic.delete().where(TopicStatistic.topic_ == Topics.select().
                                      where(Topics.name == topic_name)).execute()
        my_parser.save_topic_stat(topic_name)
