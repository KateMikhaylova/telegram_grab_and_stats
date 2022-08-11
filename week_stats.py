import re
import pymorphy2
import nltk

from nltk.corpus import stopwords
from collections import defaultdict, Counter
from telethon.tl.types import PeerUser, MessageMediaPoll
from chat_data import ChatData


class WeekStats(ChatData):
    def __init__(self, client):
        super().__init__(client)
        self.lemmatize = None
        self.n_words = None
        self.top_3_number_of_words = None

    async def get_user_by_id(self, user_id: int) -> object:
        '''
        Gets information about the user with their id.
        :param user_id: User id
        :return: user object by id <class 'telethon.tl.types.User'>
        '''
        user = await self.client.get_entity(user_id)
        return user

    def top_3(self, all_data: list) -> dict:
        '''
        :param all_data: all data from chat
        :return: top 3 commentators
        '''
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

        return result

    def get_links(self, user_ids: list) -> list:
        '''
        Replaces user ids to links.
        :param user_ids: list of user ids
        :return: list of links for the user ids
        '''
        links = []

        for user_id in user_ids:
            from_user = self.client.loop.run_until_complete(self.get_user_by_id(user_id))  # gets user information

            if from_user.username is not None:
                links += [((from_user.first_name if from_user.first_name is not None else "")
                           + " "
                           + (from_user.last_name if from_user.last_name is not None else "")).strip()
                          + f'(@{from_user.username})']
            else:
                links += ['['
                          + ((from_user.first_name if from_user.first_name is not None else "")
                             + " "
                             + (from_user.last_name if from_user.last_name is not None else "")).strip()
                          + ']'
                          + f'(tg://user?id={user_id})']
        return links

    def top_words(self, all_data: list, add_stop_words: list = []) -> dict:
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

        if not self.lemmatize:
            tokens = [token.replace('ё', 'е') for token in tokens if token not in all_stopwords]
            without_lemmatize = Counter(tokens)
            top_words = {word: quantity for word, quantity in without_lemmatize.most_common(self.n_words)}
            return top_words

        morph = pymorphy2.MorphAnalyzer()
        pymorphed_tokens = []
        for token in tokens:
            pymorphed_tokens.append(morph.parse(token)[0].normal_form)
        pymorphed_tokens = [token for token in pymorphed_tokens if token not in all_stopwords]
        pymorphed = Counter(pymorphed_tokens)
        top_words = {word.replace('ё', 'е'): quantity for word, quantity in pymorphed.most_common(self.n_words)}
        return top_words

    def polls_stats(self, all_data: list) -> dict:
        '''
        :param all_data: all data from chat
        :return: stats from polls
        '''
        polls_stats_dict = {}

        for message in all_data:
            if type(
                    message.media) == MessageMediaPoll and message.media.poll.quiz and message.media.results.results:  # checks if message is a poll and poll has the right answer and user already answered on poll

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
        return polls_stats_dict

    def stats_template(self, all_data: list, week_stats: bool, month_stats: bool, year_stats: bool) -> str:
        '''
        Template for week results
        :param all_data: all data from chat
        :return: text for week results
        '''
        top_3 = self.top_3(all_data)
        top_words = self.top_words(all_data)
        polls_stats = self.polls_stats(all_data)
        template_text = f'''
🗓Итоги {'недели' if week_stats else 'месяца' if month_stats else 'года' if year_stats else 'периода'} ({self.date_range[0]} - {self.date_range[1]})
🏆 Топ комментаторов:
🥇 {', '.join(first := sorted(top_3, key=lambda u: top_3[u])[2])
    + (number_of_words := 
       lambda pos: ' (' 
                   + str(top_3[pos]) 
                   + (' комментари' 
                      + ('й' if (str(top_3[pos])[-1] == '1' and ('0' + str(top_3[pos]))[-2] != '1')
                         else 'я' if (str(top_3[pos])[-1] in ['2', '3', '4'] and ('0' + str(top_3[pos]))[-2] != '1')
                         else 'ев') 
                      + ')') if self.top_3_number_of_words 
                         else '')(first)}
🥈 {', '.join(second := sorted(top_3, key=lambda u: top_3[u])[1]) + number_of_words(second)}
🥉 {', '.join(third := sorted(top_3, key=lambda u: top_3[u])[0]) + number_of_words(third)}

⌨ Популярные слова:
{(', '.join(sorted(top_words, key=lambda w: top_words[w], reverse=True)))}.\n'''

        for poll in polls_stats:
            template_text += f'\n📊В [тесте]({poll}) {polls_stats[poll][0]} ответили правильно {polls_stats[poll][1]}'

        return template_text
