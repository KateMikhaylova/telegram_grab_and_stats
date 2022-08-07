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
        return dict(link=[XX%, emote])

    def stats_template(self, all_data: list) -> str:
        '''
        Template for week results
        :param all_data: all data from chat
        :return: text for week results
        '''
        top_3 = self.top_3(all_data)
        top_words = self.top_words(all_data)
        polls_stats = self.polls_stats(all_data)
        template_text = f'''
🗓Итоги недели ({self.date_range[0]} - {self.date_range[1]})
🏆 Топ комментаторов:
🥇 {', '.join(sorted(top_3, key=lambda u: top_3[u])[2])}
🥈 {', '.join(sorted(top_3, key=lambda u: top_3[u])[1])}
🥉 {', '.join(sorted(top_3, key=lambda u: top_3[u])[0])}

⌨ Популярные слова:
{(', '.join(sorted(top_words, key=lambda w: top_words[w], reverse=True))).capitalize()}.\n'''

        for poll in polls_stats:
            template_text += f'\n📊В тесте({poll}) {polls_stats[poll][0]} ответили правильно {polls_stats[poll][1]}'

        return template_text
