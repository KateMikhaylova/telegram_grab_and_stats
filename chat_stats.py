import re
import pymorphy2
import nltk
import asyncio
import os
import matplotlib.pyplot as plt

from datetime import datetime
from nltk.corpus import stopwords
from collections import defaultdict, Counter
from telethon.tl.types import PeerUser, MessageMediaPoll, PeerChannel
from chat_getter import ChatGetter
from threading import Thread
from queue import Queue
from PIL import Image
from numpy import array
from wordcloud import WordCloud, ImageColorGenerator
from utils import date_range


class ChatStats(ChatGetter):
    def __init__(self, telethon_client):
        super().__init__(telethon_client)
        self.lemmatize = None
        self.n_words = None
        self.n_posts = None
        self.top_3_number_of_words = None
        self.stop_words = None
        self.top_posts_stats = None
        self.word_cloud = None
        self.average_polls_stats = None

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

    def create_word_cloud(self):
        """
        Creates word cloud based on top 200 most common words in messages. Picture for word cloud mask may be changed
        :return: None
        """
        mask = array(Image.open(os.path.join('img', 'python_logo.png')))
        word_cloud = WordCloud(mask=mask).generate_from_frequencies(self.cloud_words)

        image_colors = ImageColorGenerator(mask)
        plt.figure(frameon=False, figsize=[15, 15])
        plt.imshow(word_cloud.recolor(color_func=image_colors), interpolation='bilinear')
        plt.axis("off")
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
        plt.savefig(os.path.join(os.getcwd(), 'img', f'word_cloud.png'))

    def top_viewed_forwarded_replied(self, all_data: list, storage: Queue):
        """
        Calculates most viewed, forwarded and replied posts
        :param all_data: all data from chat
        :param storage: container for returning value
        """

        views_dict = {}
        forwards_dict = {}
        replies_dict = {}

        for message in all_data:
            if (message.from_id is None or type(message.from_id) == PeerChannel) \
                    and message.message or type(message.media) == MessageMediaPoll:
                # in the first pair of options first one takes posts if it is channel, second one posts if it is chat
                # second pair of options takes posts with texts and also polls, which don't have message attribute
                if message.views is not None:
                    if message.views not in views_dict:
                        views_dict[message.views] = [f'https://t.me/{self.tg_chat.username}/{message.id}']
                    else:
                        views_dict[message.views].append(f'https://t.me/{self.tg_chat.username}/{message.id}')

                if message.forwards is not None:
                    if message.forwards not in forwards_dict:
                        forwards_dict[message.forwards] = [f'https://t.me/{self.tg_chat.username}/{message.id}']
                    else:
                        forwards_dict[message.forwards].append(f'https://t.me/{self.tg_chat.username}/{message.id}')

                if message.replies:  # comments in channel may be restricted
                    if message.replies.replies not in replies_dict:
                        replies_dict[message.replies.replies] = [f'https://t.me/{self.tg_chat.username}/{message.id}']
                    else:
                        replies_dict[message.replies.replies].append(f'https://t.me/{self.tg_chat.username}/{message.id}')

        views = sorted(views_dict.items(), reverse=True)
        forwards = sorted(forwards_dict.items(), reverse=True)
        replies = sorted(replies_dict.items(), reverse=True)

        result = {'views': views, 'forwards': forwards, 'replies': replies}

        storage.put(result)

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
                        correct_percent = round(proportion * 100)

                        link = f'https://t.me/{self.tg_chat.username}/{message.id}'  # creates a link for post

                polls_stats_dict[link] = [correct_percent, ('🙂' if proportion > 0.5
                                                            else '😐' if proportion <= 0.5 and votes == max_votes
                                                            else '☹')]
        storage.put(polls_stats_dict)

    def text_head(self, week_stats: bool, month_stats: bool, year_stats: bool) -> str:
        """
        Creates text head for template text
        :param week_stats: if week period is chosen
        :param month_stats: if month period is chosen
        :param year_stats: if year period is chosen
        :return: text head
        """
        text = '🗓Итоги '

        if week_stats:
            text += 'недели '
        elif month_stats:
            text += 'месяца '
        elif year_stats:
            text += 'года '

        text += f"({self.date_range[0].strftime('%d/%m/%Y')} - {self.date_range[1].strftime('%d/%m/%Y')})\n\n"

        return text

    def text_top_3(self, top_3: dict) -> str:
        """
        Creates text with top 3 participants based on quantity of comments for template text
        :param top_3: dictionary with top participants
        :return: text with top 3 participants
        """
        text = '🏆 Топ комментаторов:\n'

        def comment_word_ending(position):
            text = '(' + str(top_3[position])
            text += ' комментари'

            if str(top_3[position])[-1] == '1' and ('0' + str(top_3[position]))[-2] != '1':
                text += 'й'
            elif str(top_3[position])[-1] in ['2', '3', '4'] and ('0' + str(top_3[position]))[-2] != '1':
                text += 'я'
            else:
                text += 'ев'

            text += ')'

            return text

        text += f"🥇 {', '.join(first := sorted(top_3, key=lambda u: top_3[u])[2]) + (comment_word_ending(first) if self.top_3_number_of_words else '')}\n"
        text += f"🥈 {', '.join(second := sorted(top_3, key=lambda u: top_3[u])[1]) + (comment_word_ending(second) if self.top_3_number_of_words else '')}\n"
        text += f"🥉 {', '.join(third := sorted(top_3, key=lambda u: top_3[u])[0]) + (comment_word_ending(third) if self.top_3_number_of_words else '')}\n\n"

        return text

    def text_top_words(self, top_words: dict) -> str:
        """
        Creates text with top used words for template text
        :param top_words: dictionary with top words
        :return: text with top words
        """
        text = f"⌨ Популярные слова:\n{(', '.join(sorted(top_words, key=lambda w: top_words[w], reverse=True)))}.\n"

        return text

    def text_polls_stats(self, polls_stats: dict) -> str:
        """
        Creates text with poll results for template text
        :param polls_stats: dictionary with polls stats
        :return: text with poll results
        """
        text = ''

        def test_word_ending(number: str) -> str:
            """
            :param number: quantity of polls
            :return: word with correct ending
            """
            text = number
            text += ' тест'

            if number[-1] in ['2', '3', '4'] and ('0' + number)[-2] != '1':
                text += 'а'
            else:
                text += 'ов'

            return text

        if self.average_polls_stats and len(polls_stats) > 1:
            text += f'\n📊 Было проведено {test_word_ending(str(len(polls_stats)))}, на которые в среднем было дано '
            text += f'{(percent := (round(sum(list(map(lambda poll: int(polls_stats[poll][0]), polls_stats)))/len(polls_stats))))}% правильных ответов '
            text += '🙂' if percent > 50 else '😐' if percent == 50 else '☹'
        else:
            for poll in polls_stats:
                text += f'\n📊В [тесте]({poll}) {polls_stats[poll][0]}% ответили правильно {polls_stats[poll][1]}'

        return text

    def text_posts_reactions(self, reactions_list):
        reactions = reactions_list[:self.n_posts]
        text = ''
        if len(reactions) == 0:
            return text
        if len(reactions) > 0:
            text += 'Самое большое количество реакций '
            if len(reactions[0][1]) == 1:
                text += f'({reactions[0][0]}) набрал этот [пост]({reactions[0][1][0]}).'
            elif len(reactions[0][1]) > 1:
                text += f'({reactions[0][0]}) набрали эти посты: '
                for i, post in enumerate(reactions[0][1], start=1):
                    text += f'[{i}]({post}) '
        if len(reactions) > 1:
            text += '\nСледом идут посты с количеством реакций '
            for reaction in reactions[1:]:
                text += f'\n{reaction[0]} - '
                for i, post in enumerate(reaction[1], start=1):
                    text += f'[{i}]({post}) '
        return text

    def text_top_viewed_forwarded_replied(self, top_vfr: dict) -> str:
        """
        Creates text with top viewed forwarded and replied posts for template text
        :param top_vfr: dictionary with top posts
        :return: text with top posts
        """
        views = top_vfr['views'][:self.n_posts]
        forwards = top_vfr['forwards'][:self.n_posts]
        replies = top_vfr['replies'][:self.n_posts]

        text_views = ''
        if len(views) > 0:
            text_views += '\n👀 Самое большое количество просмотров '
            if len(views[0][1]) == 1:
                text_views += f'({views[0][0]}) было у этого [поста]({views[0][1][0]}).'
            elif len(views[0][1]) > 1:
                text_views += f'({views[0][0]}) было у этих постов: '
                for i, post in enumerate(views[0][1], start=1):
                    text_views += f'[{i}]({post}) '
        if len(views) > 1:
            text_views += '\nСледом идут посты с количеством просмотров '
            for view in views[1:]:
                text_views += f'\n{view[0]} - '
                for i, post in enumerate(view[1], start=1):
                    text_views += f'[{i}]({post}) '

        text_fwd = ''
        if len(forwards) > 0:
            text_fwd += '\n📨 Самое большое количество репостов '
            if len(forwards[0][1]) == 1:
                text_fwd += f'({forwards[0][0]}) было у этого [поста]({forwards[0][1][0]}).'
            elif len(forwards[0][1]) > 1:
                text_fwd += f'({forwards[0][0]}) было у этих постов: '
                for i, post in enumerate(forwards[0][1], start=1):
                    text_fwd += f'[{i}]({post}) '
        if len(forwards) > 1:
            text_fwd += '\nСледом идут посты с количеством репостов '
            for forward in forwards[1:]:
                text_fwd += f'\n{forward[0]} - '
                for i, post in enumerate(forward[1], start=1):
                    text_fwd += f'[{i}]({post}) '

        text_replies = ''
        if len(replies) > 0:
            text_replies += '\n💬 Самое большое количество комментариев '
            if len(replies[0][1]) == 1:
                text_replies += f'({replies[0][0]}) было у этого [поста]({replies[0][1][0]}).'
            elif len(replies[0][1]) > 1:
                text_replies += f'({replies[0][0]}) было у этих постов: '
                for i, post in enumerate(replies[0][1], start=1):
                    text_replies += f'[{i}]({post}) '
        if len(replies) > 1:
            text_replies += '\nСледом идут посты с количеством комментариев '
            for reply in replies[1:]:
                text_replies += f'\n{reply[0]} - '
                for i, post in enumerate(reply[1], start=1):
                    text_replies += f'[{i}]({post}) '

        text = text_views + text_fwd + text_replies

        return text

    def text_comments_reactions(self, reactions_list):
        reactions = reactions_list[:self.n_posts]
        text = ''
        if len(reactions) == 0:
            return text
        if len(reactions) > 0:
            text += 'А еще у нас были комментарии, в которых авторы жгли не по-детски. Самое большое количество реакций '
            if len(reactions[0][1]) == 1:
                text += f'({reactions[0][0]}) набрал этот [комментарий]({reactions[0][1][0]}).'
            elif len(reactions[0][1]) > 1:
                text += f'({reactions[0][0]}) набрали эти комментарии: '
                for i, post in enumerate(reactions[0][1], start=1):
                    text += f'[{i}]({post}) '
        if len(reactions) > 1:
            text += '\nСледом идут чуть менее искрометные комментарии с количеством реакций '
            for reaction in reactions[1:]:
                text += f'\n{reaction[0]} - '
                for i, post in enumerate(reaction[1], start=1):
                    text += f'[{i}]({post}) '
        return text

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
        storage4 = Queue()

        threads = [Thread(target=self.top_3, args=[all_data, storage1, loop]),
                   Thread(target=self.top_words, args=[all_data, storage2, self.stop_words]),
                   Thread(target=self.polls_stats, args=[all_data, storage3]),
                   Thread(target=self.top_viewed_forwarded_replied, args=[all_data, storage4])]  # creating threads
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]  # waits until all threads are done

        top_3 = storage1.get()  # gets values from containers
        top_words = storage2.get()
        polls_stats = storage3.get()
        top_viewed_forwarded_replied = storage4.get()

        template_text = (self.text_head(week_stats, month_stats, year_stats)
                         + self.text_top_3(top_3)
                         + self.text_top_words(top_words)
                         + self.text_polls_stats(polls_stats)
                         + (self.text_top_viewed_forwarded_replied(top_viewed_forwarded_replied)
                         if self.top_posts_stats else ''))

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

        await self.telethon_client.send_message(tg_chat, text, link_preview=False, file=file)

    def options_update(self, n_words: int, n_posts: int, top_3_number_of_words: bool, lemmatize: bool, average_polls_stats: bool,
                       top_posts_stats: bool, word_cloud: bool, stop_words: list):
        """
        Updates optional parameters.
        :param n_words: number of words in top words list
        :param n_posts: number of posts in top posts and reactions
        :param top_3_number_of_words: top 3 number pf words checkbox position
        :param lemmatize: lemmatizes checkbox position
        :param average_polls_stats: average polls stats checkbox position
        :param top_posts_stats: top posts checkbox position
        :param word_cloud: word cloud checkbox position
        :param stop_words: stopwords list
        :return: None
        """
        self.n_words = n_words
        self.n_posts = n_posts
        self.top_3_number_of_words = top_3_number_of_words
        self.lemmatize = lemmatize
        self.average_polls_stats = average_polls_stats
        self.top_posts_stats = top_posts_stats
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
