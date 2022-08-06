from telethon.tl.types import MessageMediaPoll

from chat_data import ChatData


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
        return dict(link=number_of_messages)

    def top_words(self, all_data: list, n_words: int = 7) -> dict:
        '''
        :param all_data: all data from chat
        :param n_words: amount of words for top
        :return: top of most common words in chat
        '''
        return dict(word=number_of_reps)

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
