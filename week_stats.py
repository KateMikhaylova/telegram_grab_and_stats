from chat_data import ChatData
from telethon.tl.types import PeerUser
import re
from collections import Counter
import pymorphy2
import nltk
from nltk.corpus import stopwords


class WeekStats(ChatData):
    async def get_user_by_id(self, user_id: int) -> object:
        '''
        :param user_id: User id
        :return: user object by id <class 'telethon.tl.types.User'>
        '''
        return object

    def top_3(self, all_data: list) -> dict:
        '''
        :param all_data: all data from chat
        :return: top 3 commentators
        '''
        return dict(user_id=[first_name, last_name, user_name, number_of_messages])

    def top_words(self, all_data: list, n_words: int = 7, add_stop_words: list = [], lemmatize: bool = True) -> dict:
        '''
        :param all_data: all data from chat
        :param n_words: amount of words for top
        :param add_stop_words: list of additional words to be excluded from calculations
        :param lemmatize: if True, words will be normalized, otherwise not
        :return: top of most common words in chat
        '''
        text = ''
        for message in all_data:
            if type(message.from_id) == PeerUser and message.message:
                text += ' ' + message.message.lower()

        split_pattern = re.compile(r'[а-яёa-z]+(?:-[а-яёa-z]+)?', re.I)
        tokens = split_pattern.findall(text)

        nltk.download('stopwords')
        all_stopwords = stopwords.words("russian") + stopwords.words("english")
        all_stopwords.extend(add_stop_words)

        if not lemmatize:
            tokens = [token for token in tokens if token not in all_stopwords]
            without_lemmatize = Counter(tokens)
            top_words = {word: quantity for word, quantity in without_lemmatize.most_common(n_words)}
            return top_words

        morph = pymorphy2.MorphAnalyzer()
        pymorphed_tokens = []
        for token in tokens:
            pymorphed_tokens.append(morph.parse(token)[0].normal_form)
        pymorphed_tokens = [token for token in pymorphed_tokens if token not in all_stopwords]
        pymorphed = Counter(pymorphed_tokens)
        top_words = {word: quantity for word, quantity in pymorphed.most_common(n_words)}
        return top_words

    def polls_stats(self, all_data: list) -> dict:
        '''
        :param all_data: all data from chat
        :return: stats from polls
        '''
        return dict(link=[XX %, emote])

    def stats_template(self, all_data: list) -> str:
        '''
        Template for week results
        :param all_data: all data from chat
        :return: text for week results
        '''
        top_3 = self.top_3(all_data)
        top_words = self.top_words(all_data)
        polls_stats = self.polls_stats(all_data)
        return str