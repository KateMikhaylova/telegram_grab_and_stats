from telethon.tl.functions.messages import GetHistoryRequest


class ChatData:
    def __init__(self, client: object, date_offset: int = 7):
        '''
        :param client: <telethon.client.telegramclient.TelegramClient object at 0x000001D5C3B97E50>
        :param date_offset: number of days
        '''
        self.client = client
        self.date_range = date_offset
        self.tg_chat = None

    @property
    def date_range(self) -> list:
        '''
        :return: list of 2 dates [start of searching, now]
        '''
        return self._date_range

    @date_range.setter
    def date_range(self, date_offset: int):
        '''
        Sets list of 2 dates [start of searching, now] to self._date_range
        :param date_offset: number of days
        '''
        self._date_range = list(date_start, date_now)

    async def get_channel(self):
        '''
        Gets telegram chat and updates attribute self.tg_chat (<class 'telethon.tl.types.Channel'>)
        '''
        self.tg_chat =

    async def get_all_data(self) -> list:
        '''
        Gets all data from the chat
        :return: list of all messages (objects)
        '''

        offset_msg = 0
        limit_msg = 100

        all_messages = []
        total_messages = 0
        total_count_limit = 0

        while True:
            history = await self.client(GetHistoryRequest(peer=self.tg_chat,
                                                     offset_id=offset_msg,
                                                     offset_date=None,
                                                     add_offset=0,
                                                     limit=limit_msg,
                                                     max_id=0,
                                                     min_id=0,
                                                     hash=0
                                                     ))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                if message.date.date() >= self.date_range[0]:
                    all_messages.append(message)
                else:
                    return all_messages

            offset_msg = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break
        return all_messages

    async def get_comments_from_post(self, post) -> list:
        '''
        :return: list of comments from post
        '''
        return list(objects)

    async def send_post(self, text: str, tg_chat: str = 'me'):
        '''
        Sends post to telegram chat
        :param text: text to send
        :param tg_chat: name of telegram chat where the message will be sent
        '''
