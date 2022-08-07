from collections import defaultdict
from telethon.tl.types import PeerUser
from chat_data import ChatData


class WeekStats(ChatData):
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
            if type(message.from_id) == PeerUser and (message.message or message.media):  # checks if message was sent by user and (message is not empty or message has media file)
                message_counter[message.from_id.user_id] += 1  # counts messages for each user

        top_dict = {'top_1': [[], 0], 'top_2': [[], 0], 'top_3': [[], 0]}

        for num, user in enumerate(sorted(message_counter, key=lambda u: message_counter[u], reverse=True)):  # fills in the dictionary top_dict
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

        result = {tuple(user[0]): user[1] for user in top_dict.values()}  # creates a new dict {tuple(links): number_of_messages}

        return result

    def get_links(self, user_ids: list) -> list:
        '''
        Replaces user ids to links.
        :param user_ids: list of user ids
        :return: list of links for the user ids
        '''
        links = []

        for user_id in user_ids:
            from_user = self.client.loop.run_until_complete(self.get_user_by_id(user_id)) # gets user information

            if from_user.username is not None:
                links += [f'@{from_user.username}']
            else:
                links += ['['
                          + ((from_user.first_name if from_user.first_name is not None else "")
                             + " "
                             + (from_user.last_name if from_user.last_name is not None else "")).strip()
                          + ']'
                          + f'(tg://user?id={user_id})']
        return links

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
        return str
