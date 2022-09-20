from datetime import timedelta
from PyQt5.QtCore import pyqtBoundSignal
from telethon import TelegramClient
from telethon.tl.types import InputPeerEmpty, Channel
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest

from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types.user_and_chats.user import User
from pyrogram.types.user_and_chats.chat import Chat
from pyrogram.errors.exceptions.bad_request_400 import MsgIdInvalid

from time import sleep
import datetime


class ChatGetter:
    def __init__(self, telethon_client: TelegramClient):
        """
        :param telethon_client: telegram client
        """
        self.telethon_client = telethon_client
        self.channels = None  # list of channels
        self.tg_chat = None  # selected channel
        self.date_range = None  # date interval [date_start, date_end]

    async def get_channel(self):
        """
        Gets list of all channels and updates the attribute self.channels
        """
        channels = []
        result = await self.telethon_client(GetDialogsRequest(offset_date=None,
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
            history = await self.telethon_client(GetHistoryRequest(peer=self.tg_chat,
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
        async for message in self.telethon_client.iter_messages(self.tg_chat,
                                                                reply_to=post_id):
            comments_list.append(message)
        return comments_list

    async def get_user_by_id(self, user_id: int) -> object:
        """
        Gets information about the user with their id.
        :param user_id: User id
        :return: user object by id <class 'telethon.tl.types.User'>
        """
        user = await self.telethon_client.get_entity(user_id)
        return user

    def get_links(self, user_ids: list) -> list:
        """
        Replaces user ids to links.
        :param user_ids: list of user ids
        :return: list of links for the user ids
        """
        links = []

        for user_id in user_ids:
            from_user = self.telethon_client.loop.run_until_complete(self.get_user_by_id(user_id))  # gets user information

            if from_user.username is not None:
                links += [((from_user.first_name if from_user.first_name is not None else "")
                           + " "
                           + (from_user.last_name if from_user.last_name is not None else "")).strip()
                          + f'(@{from_user.username})']
            else:
                links += [((from_user.first_name if from_user.first_name is not None else "")
                          + " "
                          + (from_user.last_name if from_user.last_name is not None else "")).strip()
                          + f' tg://user?id={user_id}']
        return links

    def get_posts_reactions(self, pyrogram_client: Client) -> list:
        """
        Collects reactions from posts in channel/chat and/or reactions to comments to posts in channel or to all
        comments in chat
        :param pyrogram_client: pyrogram client to send requests to API
        :return: list with two lists, first one with posts reactions, second with comments reactions, if some option is
        not chosen corresponding inner list will be empty
        """
        with pyrogram_client:

            chat_id = int('-100' + str(self.tg_chat.id))
            chat = pyrogram_client.get_chat(chat_id)

            offset_msg = 0
            limit_msg = 100
            date_offset = self.date_range[1] + timedelta(days=1)
            date_offset = datetime.datetime.combine(date_offset, datetime.time())

            posts_reactions_dict = {}
            comments_reactions_dict = {}

            while True:

                messages = list(pyrogram_client.get_chat_history(chat_id=chat_id,
                                                                 limit=limit_msg,
                                                                 offset_id=offset_msg,
                                                                 offset_date=date_offset
                                                                 ))

                if not messages:
                    posts_reactions_dict = sorted(posts_reactions_dict.items(), reverse=True)[:10]
                    comments_reactions_dict = sorted(comments_reactions_dict.items(), reverse=True)[:10]
                    return [posts_reactions_dict, comments_reactions_dict]

                for message in messages:
                    message_id = message.id

                    if message.date.date() < self.date_range[0]:
                        posts_reactions_dict = sorted(posts_reactions_dict.items(), reverse=True)[:10]
                        comments_reactions_dict = sorted(comments_reactions_dict.items(), reverse=True)[:10]
                        return [posts_reactions_dict, comments_reactions_dict]

                    if self.top_posts_reactions:

                        if chat.type == ChatType.CHANNEL:
                            if message.reactions is not None:
                                reactions = 0
                                for element in message.reactions.reactions:
                                    reactions += element.count
                                if reactions not in posts_reactions_dict:
                                    posts_reactions_dict[reactions] = [f'https://t.me/{message.chat.username}/{message.id}']
                                else:
                                    posts_reactions_dict[reactions].append(f'https://t.me/{message.chat.username}/{message.id}')

                        elif chat.type == ChatType.GROUP or chat.type == ChatType.SUPERGROUP:
                            if type(message.sender_chat) == Chat and message.reactions is not None:
                                reactions = 0
                                for element in message.reactions.reactions:
                                    reactions += element.count
                                if reactions not in posts_reactions_dict:
                                    posts_reactions_dict[reactions] = [f'https://t.me/{message.chat.username}/{message.id}']
                                else:
                                    posts_reactions_dict[reactions].append(f'https://t.me/{message.chat.username}/{message.id}')

                    if self.top_comments_reactions:

                        if chat.type == ChatType.CHANNEL:
                            # если к отдельному посту отключены комментарии, получаем ошибку. В pythontalk например есть
                            # такой пост https://t.me/pythontalk_ru/97. Или обходить ее вручную (if message.id == 97:
                            # continue, но сколько таких теоретически может быть) или try-except. Да и без try-except в
                            # цикле сбор комментариев по постам в пирограме очень медленный (его еще приходится отправлять
                            # поспать после каждого такого запроса, иначе pyrogram.errors.exceptions.flood_420.FloodWait),
                            # по-хорошему лучше для оценки лайков комменты собирать в чате конечно. Опять же, поиск внутри
                            # постов канала все равно даст в id сообщений ссылки на сообщения чата и ссылка на топовое все
                            # равно приведет в чат
                            sleep(1)
                            try:
                                for comment in pyrogram_client.get_discussion_replies(chat_id=chat_id,
                                                                                      message_id=message.id):
                                    if comment.reactions is not None:
                                        reactions = 0
                                        for element in comment.reactions.reactions:
                                            reactions += element.count
                                        if reactions not in comments_reactions_dict:
                                            comments_reactions_dict[reactions] = [
                                                f'https://t.me/{comment.chat.username}/{comment.id}']
                                        else:
                                            comments_reactions_dict[reactions].append(
                                                f'https://t.me/{comment.chat.username}/{comment.id}')
                            except MsgIdInvalid:
                                pass

                        elif chat.type == ChatType.GROUP or chat.type == ChatType.SUPERGROUP:

                            if type(message.from_user) == User and message.reactions is not None:
                                reactions = 0
                                for element in message.reactions.reactions:
                                    reactions += element.count
                                if reactions not in comments_reactions_dict:
                                    comments_reactions_dict[reactions] = [f'https://t.me/{message.chat.username}/{message.id}']
                                else:
                                    comments_reactions_dict[reactions].append(
                                        f'https://t.me/{message.chat.username}/{message.id}')

                offset_msg = message_id
