from telethon.tl.types import InputPeerEmpty, Channel
from telethon.tl.functions.messages import GetDialogsRequest


class ChatData:
    def __init__(self, client: object, date_offset: int = 7):
        '''
        :param client: <class 'telethon.client.telegramclient.TelegramClient'>
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
        channels = []
        result = await self.client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=100,
            hash=0
        ))

        for channel in result.chats:
            if type(channel) == Channel:
                channels.append(channel)

        channels.sort(key=lambda c: c.title.lower())

        print('\nКаналы:')
        for num, channel in enumerate(channels, start=1):
            print(str(num) + ' - ' + channel.title)

        group_index = input('\nВведите номер канала: ')

        while True:
            if group_index.isdigit() and 1 <= int(group_index) <= len(channels):
                self.tg_chat = channels[int(group_index) - 1]
                break
            else:
                group_index = input('\nВведен неподходящий номер, попробуйте еще раз: ')


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
