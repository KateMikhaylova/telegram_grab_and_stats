from datetime import timedelta
from PyQt5.QtCore import pyqtBoundSignal
from telethon import TelegramClient
from telethon.tl.types import InputPeerEmpty, Channel
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest


class ChatGetter:
    def __init__(self, client: TelegramClient):
        """
        :param client: telegram client
        """
        self.client = client
        self.channels = None  # list of channels
        self.tg_chat = None  # selected channel
        self.date_range = None  # date interval [date_start, date_end]

    async def get_channel(self):
        """
        Gets list of all channels and updates the attribute self.channels
        """
        channels = []
        result = await self.client(GetDialogsRequest(offset_date=None,
                                                     offset_id=0,
                                                     offset_peer=InputPeerEmpty(),
                                                     limit=100,
                                                     hash=0
                                                     ))

        for channel in result.chats:
            if type(channel) == Channel:
                channels.append(channel)

        channels.sort(key=lambda c: c.title.lower())
        self.channels = channels

    async def get_all_data(self, any_signal: pyqtBoundSignal) -> list:
        """
        Gets all data from the chat
        :param any_signal: value for GUI progress bar
        :return: list of messages (objects)
        """
        broadcast_channel = self.tg_chat.broadcast

        offset_msg = 0
        limit_msg = 100
        date_offset = self.date_range[1] + timedelta(days=1)

        previous_date = self.date_range[1]
        progress_bar_value = 0

        all_messages = []

        while True:
            history = await self.client(GetHistoryRequest(peer=self.tg_chat,
                                                          offset_id=offset_msg,
                                                          offset_date=date_offset,
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
                    if previous_date.day != message.date.date().day:
                        progress_bar_value += (previous_date - message.date.date()).days
                        any_signal.emit(progress_bar_value)  # Sends the value for the GUI progress bar
                        previous_date = message.date.date()

                    all_messages.append(message)
                    if broadcast_channel and message.replies is not None and message.replies.replies:
                        all_messages.extend(await self.get_comments_from_post(message.id))
                else:
                    return all_messages

            offset_msg = messages[-1].id

    async def get_comments_from_post(self, post_id: int) -> list:
        """
        Gets all comments from the particular channel post
        :param post_id: channel post id
        :return: list of comments from post
        """
        comments_list = []
        async for message in self.client.iter_messages(self.tg_chat,
                                                       reply_to=post_id):
            comments_list.append(message)
        return comments_list

    async def get_user_by_id(self, user_id: int) -> object:
        """
        Gets information about the user with their id.
        :param user_id: User id
        :return: user object by id <class 'telethon.tl.types.User'>
        """
        user = await self.client.get_entity(user_id)
        return user

    def get_links(self, user_ids: list) -> list:
        """
        Replaces user ids to links.
        :param user_ids: list of user ids
        :return: list of links for the user ids
        """
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
