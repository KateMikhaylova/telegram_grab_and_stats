class ChatData:
    def __init__(self, date_offset: int = 7):
        '''
        :param date_offset: number of days
        '''
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
        return list(objects)

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
