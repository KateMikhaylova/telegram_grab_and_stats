from datetime import datetime, timedelta, timezone
from telethon.tl.types import InputPeerEmpty, Channel
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest


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
        date_now = datetime.now(timezone.utc).date()
        date_start = date_now - timedelta(days=date_offset)
        self._date_range = [date_start, date_now]

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
        broadcast_channel = self.tg_chat.broadcast

        offset_msg = 0
        limit_msg = 100

        all_messages = []

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
                return all_messages

            messages = history.messages

            for message in messages:
                if message.date.date() >= self.date_range[0]:
                    all_messages.append(message)
                    if broadcast_channel and message.replies is not None and message.replies.replies:
                        all_messages.extend(await self.get_comments_from_post(message.id))
                else:
                    return all_messages

            offset_msg = messages[-1].id

    async def get_comments_from_post(self, post_id: int) -> list:
        '''
        Gets all comments from the particular channel post
        :param post_id: channel post id
        :return: list of comments from post
        '''
        comments_list = []
        async for message in self.client.iter_messages(self.tg_chat,
                                                       reply_to=post_id):
            comments_list.append(message)
        return comments_list

    async def send_post(self, text: str, tg_chat: str = 'me'):
        '''
        Sends post to telegram chat
        :param text: text to send
        :param tg_chat: name of telegram chat where the message will be sent
        '''
