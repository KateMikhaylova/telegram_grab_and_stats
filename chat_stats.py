import re
import pymorphy2
import nltk
import asyncio
import os
import matplotlib.pyplot as plt

from datetime import datetime
from nltk.corpus import stopwords
from collections import defaultdict, Counter
from telethon.tl.types import PeerUser, MessageMediaPoll
from chat_getter import ChatGetter
from threading import Thread
from queue import Queue
from PIL import Image
from numpy import array
from wordcloud import WordCloud, ImageColorGenerator
from utils import date_range


class ChatStats(ChatGetter):
    def __init__(self, client):
        super().__init__(client)
        self.lemmatize = None
        self.n_words = None
        self.top_3_number_of_words = None
        self.stop_words = None
        self.word_cloud = None

    def top_3(self, all_data: list, storage: Queue, loop):
        """
        Calculates top 3 commentators.
        :param all_data: all data from chat
        :param storage: container for returning value
        :param loop: event loop
        """
        asyncio.set_event_loop(loop)

        message_counter = defaultdict(int)

        for message in all_data:
            if type(message.from_id) == PeerUser and (
                    message.message or message.media):  # checks if message was sent by user and (message is not empty or message has media file)
                message_counter[message.from_id.user_id] += 1  # counts messages for each user

        top_dict = {'top_1': [[], 0], 'top_2': [[], 0], 'top_3': [[], 0]}

        for num, user in enumerate(sorted(message_counter, key=lambda u: message_counter[u],
                                          reverse=True)):  # fills in the dictionary top_dict
            if not top_dict['top_1'][0] or message_counter[user] == top_dict['top_1'][1]:
                top_dict['top_1'][0] += [user]
                if not top_dict['top_1'][1]:
                    top_dict['top_1'][1] += message_counter[user]
            elif not top_dict['top_2'][0] or message_counter[user] == top_dict['top_2'][1]:
                top_dict['top_2'][0] += [user]
                if not top_dict['top_2'][1]:
                    top_dict['top_2'][1] += message_counter[user]
            elif not top_dict['top_3'][0] or message_counter[user] == top_dict['top_3'][1]:
                top_dict['top_3'][0] += [user]
                if not top_dict['top_3'][1]:
                    top_dict['top_3'][1] += message_counter[user]
            else:
                break

        for position in top_dict:  # replaces ids to links
            top_dict[position][0] = self.get_links(top_dict[position][0])

        result = {tuple(user[0]): user[1] for user in
                  top_dict.values()}  # creates a new dict {tuple(links): number_of_messages}

        storage.put(result)

    def top_words(self, all_data: list, storage: Queue, add_stop_words: list):
        """
        Calculates most common words.
        :param all_data: all data from chat
        :param storage: container for returning value
        :param add_stop_words: list of additional words to be excluded from calculations
        """
        text = ''
        for message in all_data:
            if type(message.from_id) == PeerUser and message.message:
                text += ' ' + message.message.lower()

        split_pattern = re.compile(r'[а-яёa-z]+(?:-[а-яёa-z]+)?', re.I)
        tokens = split_pattern.findall(text)

        nltk.download('stopwords')
        all_stopwords = stopwords.words("russian") + stopwords.words("english")
        all_stopwords.extend(add_stop_words)

        if not self.lemmatize:
            tokens = [token.replace('ё', 'е') for token in tokens if token not in all_stopwords]
            without_lemmatize = Counter(tokens)

            if self.word_cloud:
                self.cloud_words = {word.replace('ё', 'е'): quantity
                                    for word, quantity in without_lemmatize.most_common(200)}

            top_words = {word: quantity for word, quantity in without_lemmatize.most_common(self.n_words)}
            storage.put(top_words)
        else:
            morph = pymorphy2.MorphAnalyzer()
            pymorphed_tokens = []
            for token in tokens:
                pymorphed_tokens.append(morph.parse(token)[0].normal_form)
            pymorphed_tokens = [token for token in pymorphed_tokens if token not in all_stopwords]
            pymorphed = Counter(pymorphed_tokens)

            if self.word_cloud:
                self.cloud_words = {word.replace('ё', 'е'): quantity for word, quantity in pymorphed.most_common(200)}

            top_words = {word.replace('ё', 'е'): quantity for word, quantity in pymorphed.most_common(self.n_words)}
            storage.put(top_words)

        if self.word_cloud:
            self.create_word_cloud()

    def create_word_cloud(self) -> None:
        '''
        Creates word cloud based on top 200 most common words in messages. Picture for word cloud mask may be changed
        :return: None
        '''
        mask = array(Image.open(os.path.join('img', 'python_logo.png')))
        word_cloud = WordCloud(mask=mask).generate_from_frequencies(self.cloud_words)

        image_colors = ImageColorGenerator(mask)
        plt.figure(frameon=False, figsize=[15, 15])
        plt.imshow(word_cloud.recolor(color_func=image_colors), interpolation='bilinear')
        plt.axis("off")
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
        plt.savefig(os.path.join(os.getcwd(), 'img', f'word_cloud.png'))

    def polls_stats(self, all_data: list, storage: Queue):
        """
        Gets polls stats.
        :param all_data: all data from chat
        :param storage: container for returning value
        """
        polls_stats_dict = {}

        for message in all_data:
            if (type(message.media) == MessageMediaPoll
                    and message.media.poll.quiz
                    and message.media.results.results):  # checks if message is a poll and poll has the right answer and user already answered on poll

                max_votes = 0  # most common option to choose

                for option in message.media.results.results:
                    if option.voters > max_votes:
                        max_votes = option.voters

                    if option.correct:  # checks if the option is the correct one
                        votes = option.voters

                        proportion = votes / message.media.results.total_voters
                        correct_percent = f'{round(proportion * 100)}%'

                        link = f'https://t.me/{self.tg_chat.username}/{message.id}'  # creates a link for post

                polls_stats_dict[link] = [correct_percent, ('🙂' if proportion > 0.5
                                                            else '😐' if proportion <= 0.5 and votes == max_votes
                                                            else '☹')]
        storage.put(polls_stats_dict)

    def stats_template(self, all_data: list, week_stats: bool, month_stats: bool, year_stats: bool, loop) -> str:
        """
        Creates text for week results
        :param all_data: all data from chat
        :param week_stats: position of GUI 'box_week_statistic'
        :param month_stats: position of GUI 'box_month_statistic'
        :param year_stats: position of GUI 'box_year_statistic'
        :param loop: event loop
        """
        storage1 = Queue()  # creates containers for storing values
        storage2 = Queue()
        storage3 = Queue()

        threads = [Thread(target=self.top_3, args=[all_data, storage1, loop]),
                   Thread(target=self.top_words, args=[all_data, storage2, self.stop_words]),
                   Thread(target=self.polls_stats, args=[all_data, storage3])]  # creating threads
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]  # waits until all threads are done

        top_3 = storage1.get()  # gets values from containers
        top_words = storage2.get()
        polls_stats = storage3.get()

        template_text = f'''
🗓Итоги {'недели' if week_stats else 'месяца' if month_stats else 'года' if year_stats else 'периода'} ({self.date_range[0].strftime('%d/%m/%Y')} - {self.date_range[1].strftime('%d/%m/%Y')})
🏆 Топ комментаторов:
🥇 {', '.join(first := sorted(top_3, key=lambda u: top_3[u])[2])
    + (number_of_words :=
       lambda pos: ' ('
                   + str(top_3[pos])
                   + (' комментари'
                      + ('й' if (str(top_3[pos])[-1] == '1' and ('0' + str(top_3[pos]))[-2] != '1')
                         else 'я' if (str(top_3[pos])[-1] in ['2', '3', '4'] and ('0' + str(top_3[pos]))[-2] != '1')
                         else 'ев') + ')') if self.top_3_number_of_words
                         else '')(first)}
🥈 {', '.join(second := sorted(top_3, key=lambda u: top_3[u])[1]) + number_of_words(second)}
🥉 {', '.join(third := sorted(top_3, key=lambda u: top_3[u])[0]) + number_of_words(third)}

⌨ Популярные слова:
{(', '.join(sorted(top_words, key=lambda w: top_words[w], reverse=True)))}.\n'''

        for poll in polls_stats:
            template_text += f'\n📊В [тесте]({poll}) {polls_stats[poll][0]} ответили правильно {polls_stats[poll][1]}'

        return template_text

    async def send_post(self, text: str, tg_chat: str = 'me'):
        """
        Sends post to telegram chat
        :param text: text to send
        :param tg_chat: name of telegram chat where the message will be sent
        """

        if self.word_cloud and self.cloud_words:
            file = os.path.join('img', 'word_cloud.png')
        else:
            file = None

        await self.client.send_message(tg_chat, text, link_preview=False, file=file)

    def options_update(self, n_words: int, top_3_number_of_words: bool, lemmatize: bool, word_cloud: bool, stop_words: list):
        """
        Updates optional parameters.
        :param n_words: number of words in top words list
        :param top_3_number_of_words: top 3 number pf words checkbox position
        :param lemmatize: lemmatizes checkbox position
        :param word_cloud: word cloud checkbox position
        :param stop_words: stopwords list
        :return: None
        """
        self.n_words = n_words
        self.top_3_number_of_words = top_3_number_of_words
        self.lemmatize = lemmatize
        self.word_cloud = word_cloud
        self.stop_words = stop_words
        self.cloud_words = None  # words for cloud words

    def date_update(self, week_number: int, month_number: int, year_number: int,
                    custom_date_start: list, custom_date_end: list,
                    week_statistic: bool, month_statistic: bool, year_statistic: bool, custom_statistic: bool):
        """
        Updates the attribute self.date_range
        :param week_number: week number
        :param month_number: month number
        :param year_number: year number
        :param custom_date_start: custom date start - (year, month, day)
        :param custom_date_end: custom date end - (year, month, day)
        :param week_statistic: week statistic checkbox position
        :param month_statistic: month statistic checkbox position
        :param year_statistic: year statistic checkbox position
        :param custom_statistic: custom statistic checkbox position
        :return:
        """
        if custom_statistic:
            self.date_range = [datetime(*custom_date_start).date(),
                               datetime(*custom_date_end).date()]  # sets custom date range
        else:
            self.date_range = date_range(week_number, month_number, year_number,
                                         week_statistic, month_statistic, year_statistic)
